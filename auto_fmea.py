import flet as ft
import os
import json
import uuid
import pandas as pd

from datetime import datetime, timedelta

CONFIG_FILE = "fmea_config.json"
LOG_FILE = "fmea_log.json"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

GOLD = "#C9A632"
BLACK = "#000000"
DARK_GRAY = "#1e1e1e"
TEXT_COLOR = "#f5f5f5"

config = load_json(CONFIG_FILE, {"entries": []})
logs = load_json(LOG_FILE, [])
now = datetime.now()
logs = [log for log in logs if not (log['action'] == 'deleted' and now - datetime.strptime(log['timestamp'], DATE_FORMAT) > timedelta(days=30))]
save_json(LOG_FILE, logs)

def main(page: ft.Page):
    page.window.maximized = True
    page.title = "Decimoni Dataworks - Análise de Modo de Falha e Efeitos"
    

    page.bgcolor = DARK_GRAY
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.START

    modo = ft.TextField(label="Modo de Falha", width=150)
    efeito = ft.TextField(label="Efeito", width=150)
    causa = ft.TextField(label="Causa", width=150)
    item = ft.TextField(label="Item", width=150)
    g = ft.TextField(label="Gravidade (1-10)", width=100)
    o = ft.TextField(label="Ocorrência (1-10)", width=100)
    d = ft.TextField(label="Detecção (1-10)", width=100)
    acao = ft.TextField(label="Ação", width=300, multiline=True, height=60)

    picker = ft.FilePicker()
    page.overlay.append(picker)

    active_table_container = ft.Container(border=ft.border.all(2, GOLD), padding=5)
    trash_table_container = ft.Container(border=ft.border.all(2, GOLD), padding=5)
    trash_selection = {}
    edit_mode = {'active': False, 'id': None}
    sort_column = "rpn"
    sort_ascending = False

    def log_action(entry_id, action, full_data):
        logs.append({
            'id': entry_id,
            'action': action,
            'timestamp': datetime.now().strftime(DATE_FORMAT),
            'data': full_data
        })
        save_json(LOG_FILE, logs)

    def save_config():
        save_json(CONFIG_FILE, config)
    
    def change_sort(column_key):
        nonlocal sort_column, sort_ascending
        if sort_column == column_key:
            sort_ascending = not sort_ascending
        else:
            sort_column = column_key
            sort_ascending = True
        refresh_active_table()


    def load_form(entry):
        modo.value = entry['modo']
        efeito.value = entry['efeito']
        causa.value = entry['causa']
        item.value = entry['item']
        g.value = str(entry['g'])
        o.value = str(entry['o'])
        d.value = str(entry['d'])
        acao.value = entry['acao']
        add_btn.text = "Salvar Alterações"
        page.update()

    def clear_form():
        for f in [modo, efeito, causa, item, g, o, d, acao]:
            f.value = ""
        edit_mode['active'] = False
        edit_mode['id'] = None
        add_btn.text = "Adicionar Entrada"
        page.update()

    def start_edit(entry_id):
        for entry in config['entries']:
            if entry['id'] == entry_id:
                load_form(entry)
                edit_mode['active'] = True
                edit_mode['id'] = entry_id
                break

    def refresh_active_table():
        non_deleted = [e for e in config['entries'] if not e.get('deleted')]
        sorted_entries = sorted(non_deleted, key=lambda x: x.get(sort_column, ""), reverse=not sort_ascending)

        def sort_button(label, column_key):
            arrow = "▲" if sort_column == column_key and sort_ascending else "▼"
            return ft.Container(
                alignment=ft.alignment.center,
                padding=5,
                content=ft.TextButton(
                    text=f"{arrow} {label}",
                    on_click=lambda e: change_sort(column_key),
                    style=ft.ButtonStyle(
                        color=ft.colors.YELLOW_500,
                        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=12),
                    )
                )
            )


        rows = []
        for entry in sorted_entries:
            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(entry.get('item', ""), color=TEXT_COLOR)),
                    ft.DataCell(ft.Text(entry.get('modo', ""), color=TEXT_COLOR)),
                    ft.DataCell(ft.Text(entry.get('efeito', ""), color=TEXT_COLOR)),
                    ft.DataCell(ft.Text(entry.get('causa', ""), color=TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(entry.get('g', '')), color=TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(entry.get('o', '')), color=TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(entry.get('d', '')), color=TEXT_COLOR)),
                    ft.DataCell(ft.Text(str(entry.get('rpn', '')), color=TEXT_COLOR)),
                    ft.DataCell(ft.Text(entry.get('acao', ""), color=TEXT_COLOR)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color=GOLD, on_click=lambda e, id=entry['id']: start_edit(id)),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_color=GOLD, on_click=lambda e, id=entry['id']: delete_entry(id)),
                    ]))
                ])
            )

        table = ft.DataTable(
            show_checkbox_column=False,
            heading_row_color=BLACK,
            columns=[
                ft.DataColumn(sort_button("Item", "item")),
                ft.DataColumn(sort_button("Modo", "modo")),
                ft.DataColumn(sort_button("Efeito", "efeito")),
                ft.DataColumn(sort_button("Causa", "causa")),
                ft.DataColumn(sort_button("G", "g")),
                ft.DataColumn(sort_button("O", "o")),
                ft.DataColumn(sort_button("D", "d")),
                ft.DataColumn(sort_button("RPN", "rpn")),
                ft.DataColumn(ft.Text("Ação", color=TEXT_COLOR)),
                ft.DataColumn(ft.Text("Ações", color=TEXT_COLOR)),
            ],
            rows=rows,
        )
        active_table_container.content = table
        page.update()

    def refresh_trash_table():
        rows = []
        trash_selection.clear()
        for entry in config['entries']:
            if entry.get('deleted'):
                cb = ft.Checkbox()
                trash_selection[entry['id']] = cb
                rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(cb),
                        ft.DataCell(ft.Text(entry.get('item', ""), color=TEXT_COLOR)),
                        ft.DataCell(ft.Text(entry.get('modo', ""), color=TEXT_COLOR)),
                        ft.DataCell(ft.Text(entry.get('efeito', ""), color=TEXT_COLOR)),
                        ft.DataCell(ft.Text(entry.get('acao', ""), color=TEXT_COLOR)),
                        ft.DataCell(
                            ft.IconButton(icon=ft.Icons.REFRESH, on_click=lambda e, id=entry['id']: restore_entry(id), icon_color=GOLD)),
                        ft.DataCell(
                            ft.IconButton(icon=ft.Icons.DELETE_FOREVER, on_click=lambda e, id=entry['id']: delete_forever(id), icon_color=GOLD))
                    ])
                )
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Sel.", color=GOLD)),
                ft.DataColumn(ft.Text("Item", color=GOLD)),
                ft.DataColumn(ft.Text("Modo", color=GOLD)),
                ft.DataColumn(ft.Text("Efeito", color=GOLD)),
                ft.DataColumn(ft.Text("Ação", color=GOLD)),
                ft.DataColumn(ft.Text("Restaurar", color=GOLD)),
                ft.DataColumn(ft.Text("Excluir", color=GOLD)),
            ],
            rows=rows
        )
        trash_table_container.content = table
        page.update()

    table_view = ft.Container()

    def add_entry(e):
        try:
            gi = int(g.value); oi = int(o.value); di = int(d.value)
        except:
            page.snack_bar = ft.SnackBar(ft.Text("G, O e D devem ser números"))
            page.snack_bar.open = True
            page.update()
            return
        rpn = gi * oi * di
        now_str = datetime.now().strftime(DATE_FORMAT)

        if edit_mode['active']:
            for entry in config['entries']:
                if entry['id'] == edit_mode['id']:
                    entry.update({
                        'modo': modo.value,
                        'efeito': efeito.value,
                        'causa': causa.value,
                        'item': item.value,
                        'g': gi, 'o': oi, 'd': di,
                        'rpn': rpn,
                        'acao': acao.value,
                        'last_modified': now_str
                    })
                    log_action(entry['id'], 'edited', entry)
                    break
        else:
            entry_id = str(uuid.uuid4())
            entry = {
                'id': entry_id,
                'modo': modo.value,
                'efeito': efeito.value,
                'causa': causa.value,
                'item': item.value,
                'g': gi, 'o': oi, 'd': di,
                'rpn': rpn,
                'acao': acao.value,
                'created_at': now_str,
                'last_modified': now_str,
                'deleted': False
            }
            config['entries'].append(entry)
            log_action(entry_id, 'created', entry)

        save_config()
        clear_form()
        refresh_active_table()

    def delete_entry(entry_id):
        for entry in config['entries']:
            if entry['id'] == entry_id:
                entry['deleted'] = True
                entry['deleted_at'] = datetime.now().strftime(DATE_FORMAT)
                log_action(entry_id, 'deleted', entry)
                save_config()
                break
        refresh_active_table()
        refresh_trash_table()

    def restore_entry(entry_id):
        for entry in config['entries']:
            if entry['id'] == entry_id:
                entry['deleted'] = False
                entry.pop('deleted_at', None)
                entry['last_modified'] = datetime.now().strftime(DATE_FORMAT)
                log_action(entry_id, 'restored', entry)
                save_config()
                break
        refresh_active_table()
        refresh_trash_table()

    def delete_forever(entry_id):
        for entry in config['entries']:
            if entry['id'] == entry_id:
                log_action(entry_id, 'permanently_deleted', entry)
        config['entries'] = [e for e in config['entries'] if e['id'] != entry_id]
        save_config()
        refresh_trash_table()

    def export_to_excel(e):
        def on_result(ev: ft.FilePickerResultEvent):
            if not ev.path:
                return

            ext = os.path.splitext(ev.path)[1].lower()
            df = pd.DataFrame(config["entries"])
            df = df.rename(columns={
                "item": "Item", "modo": "Modo de Falha", "efeito": "Efeito", "causa": "Causa",
                "g": "Gravidade", "o": "Ocorrência", "d": "Detecção", "rpn": "RPN",
                "acao": "Ação", "created_at": "Criado em", "last_modified": "Modificado em", "deleted": "Excluído"
            })
            for col in ["Criado em", "Modificado em"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%d.%m.%Y")

            try:
                if ext == ".xlsx":
                    df.to_excel(ev.path, index=False, sheet_name="itens")
                elif ext == ".csv":
                    df.to_csv(ev.path, index=False, sep=";")
                elif ext == ".pdf":
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(8, len(df) * 0.5))
                    ax.axis("tight")
                    ax.axis("off")
                    ax.table(cellText=df.values, colLabels=df.columns, loc="center")
                    plt.savefig(ev.path, bbox_inches="tight")
                    plt.close()
                elif ext == ".png":
                    import dataframe_image as dfi
                    dfi.export(df, ev.path)
                else:
                    raise ValueError("Unsupported file extension")

                page.snack_bar = ft.SnackBar(ft.Text(f"Exportado com sucesso para {ext.upper()}"))
                page.snack_bar.open = True
            except Exception as err:
                page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao exportar: {err}"))
                page.snack_bar.open = True

            page.update()

        picker.on_result = on_result

        picker.save_file(
            dialog_title="Exportar Arquivo (digite o nome com .xlsx, .csv, .png ou .pdf)",
            file_type="any"  # <- to allow manual extensions
        )

    def generate_histograms(e):
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd

            df = pd.DataFrame(config["entries"])
            df = df[~df["deleted"]]

            if df.empty:
                page.snack_bar = ft.SnackBar(ft.Text("Nenhuma entrada para gerar histogramas."))
                page.snack_bar.open = True
                page.update()
                return

            items = df["item"]
            g_vals = df["g"]
            o_vals = df["o"]
            d_vals = df["d"]
            rpn_vals = df["rpn"]

            x = np.arange(len(items))
            width = 0.25

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

            # GOD histogram
            bars_g = ax1.bar(x - width, g_vals, width, label='G')
            bars_o = ax1.bar(x, o_vals, width, label='O')
            bars_d = ax1.bar(x + width, d_vals, width, label='D')

            for bars in [bars_g, bars_o, bars_d]:
                for bar in bars:
                    height = bar.get_height()
                    ax1.annotate(f"{height}", xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)

            ax1.set_title("Gravidade, Ocorrência e Detecção por Item")
            ax1.set_ylabel("Índice")
            ax1.set_xticks(x)
            ax1.set_xticklabels(items, rotation=45, ha="right")
            ax1.grid(True, axis='y', linestyle='--', alpha=0.5)
            ax1.legend()

            # RPN histogram
            bars_rpn = ax2.bar(x, rpn_vals, width*3, color="#C9A632")

            for bar in bars_rpn:
                height = bar.get_height()
                ax2.annotate(f"{height}", xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)

            ax2.set_title("RPN Total por Item")
            ax2.set_ylabel("RPN")
            ax2.set_xticks(x)
            ax2.set_xticklabels(items, rotation=45, ha="right")
            ax2.grid(True, axis='y', linestyle='--', alpha=0.5)

            plt.tight_layout()
            plt.show()

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao gerar gráficos: {ex}"))
            page.snack_bar.open = True
            page.update()







    add_btn = ft.ElevatedButton("Adicionar Entrada", bgcolor=GOLD, color=BLACK, on_click=add_entry)
    export_btn = ft.ElevatedButton("Exportar", bgcolor=GOLD, color=BLACK, on_click=export_to_excel)
    generate_btn = ft.ElevatedButton("Gerar Gráficos", on_click=generate_histograms, bgcolor=GOLD, color=BLACK)



    view_switch = ft.Switch(label="Lixeira", value=False)

    def restore_selected(e):
        for eid, cb in trash_selection.items():
            if cb.value:
                restore_entry(eid)

    def delete_selected(e):
        for eid, cb in list(trash_selection.items()):
            if cb.value:
                delete_forever(eid)

    def update_view(e=None):
        if view_switch.value:
            table_view.content = ft.Column([
                ft.Row([
                    ft.ElevatedButton("Restaurar Selecionados", on_click=restore_selected, bgcolor=GOLD, color=BLACK),
                    ft.ElevatedButton("Deletar Selecionados", on_click=delete_selected, bgcolor=GOLD, color=BLACK)
                ], spacing=10),
                trash_table_container
            ])
        else:
            table_view.content = active_table_container

        page.update()




    view_switch.on_change = update_view

    content = ft.Row([
        ft.Column([
            ft.Text("Decimoni Dataworks FMEA Manager", style="headlineMedium",color=GOLD,weight="bold"),
            ft.Row([item, modo, efeito, causa, g, o, d], spacing=20),
            acao,
            ft.Row([add_btn, export_btn, generate_btn, view_switch], spacing=15),
            table_view  # ✅ cleaner way

        ], spacing=10, expand=3),
    ])



    page.add(content)
    refresh_active_table()
    refresh_trash_table()
    update_view()

if __name__ == "__main__":
    ft.app(target=main)
