#Abaixo são importadas todas as bibliotecas usadas e suas respectivas dependências.
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner

# Para está ver~saod e prótotipo a função a seguir serv de uso para simular um Banco de Dados da aplicação.
stock_data = []


#Abaixo está a base dados que deve ser preenchida por outro módulo com as informações genéricas de nutrição de cada alimento para que o sistema possa ter uma idéia dos dados a serem preenchidos.
nutrition_data = {
    'Arroz': {'proteins': 2.5, 'carbohydrates': 28},
    #A idéia é que aqui fique uma lista com variados alimentos.
}

#Separamos estas cartegorias de produto, mas apenas a cartegoria 'Alimentos' tem acesso a base de dados nutricional.
categories = ['Alimentos', 'Limpeza', 'Eletrônicos', 'Outros']

#Tela interna do controle de estouque, onde possibilita adicionar, atualizar ou remover um item.
class StockItemScreen(BoxLayout):
    def __init__(self, main_screen, item=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.main_screen = main_screen
        self.item = item  # item será None ao adicionar, ou um dicionário ao editar

        # Campo de nome do item
        self.item_name_input = TextInput(text=item['name'] if item else "", hint_text="Nome do item", size_hint=(1, 0.2))
        self.add_widget(self.item_name_input)

        # Campo de quantidade
        self.item_quantity_input = TextInput(text=str(item['quantity']) if item else "", hint_text="Quantidade (kg)", size_hint=(1, 0.2))
        self.add_widget(self.item_quantity_input)

        # Spinner para escolher a categoria
        self.category_spinner = Spinner(text=item['category'] if item else 'Selecione a categoria', values=categories, size_hint=(1, 0.2))
        self.category_spinner.bind(text=self.on_category_select)
        self.add_widget(self.category_spinner)

        # Campos adicionais para alimentos (macronutrientes)
        self.protein_input = None
        self.carb_input = None

        # Botão para salvar o item
        save_button = Button(text="Salvar", size_hint=(1, 0.2), background_color=(0.2, 0.6, 1, 1))
        save_button.bind(on_press=self.save_item)
        self.add_widget(save_button)

        # Botão para cancelar
        cancel_button = Button(text="Cancelar", size_hint=(1, 0.2), background_color=(1, 0.2, 0.2, 1))
        cancel_button.bind(on_press=self.cancel)
        self.add_widget(cancel_button)

        # Se o item for da categoria "Alimentos", mostra os campos de macronutrientes
        if item and item['category'] == 'Alimentos':
            self.show_macronutrient_fields(item)

    def on_category_select(self, spinner, text):
        if text == 'Alimentos':
            self.show_macronutrient_fields()
        else:
            self.hide_macronutrient_fields()

    def show_macronutrient_fields(self, item=None):
        # Verifica se o item é um alimento conhecido e faz o cálculo automático
        if self.item_name_input.text in nutrition_data:
            item_name = self.item_name_input.text
            quantity_in_kg = float(self.item_quantity_input.text) if self.item_quantity_input.text else 1

            proteins_per_100g = nutrition_data[item_name]['proteins']
            carbs_per_100g = nutrition_data[item_name]['carbohydrates']

            total_proteins = (quantity_in_kg * 1000 / 100) * proteins_per_100g
            total_carbs = (quantity_in_kg * 1000 / 100) * carbs_per_100g

            self.protein_input = TextInput(text=f"{total_proteins:.2f}", hint_text="Proteínas (g)", size_hint=(1, 0.2), readonly=True)
            self.carb_input = TextInput(text=f"{total_carbs:.2f}", hint_text="Carboidratos (g)", size_hint=(1, 0.2), readonly=True)

        else:
            self.protein_input = TextInput(hint_text="Proteínas (g)", size_hint=(1, 0.2))
            self.carb_input = TextInput(hint_text="Carboidratos (g)", size_hint=(1, 0.2))

        self.add_widget(self.protein_input)
        self.add_widget(self.carb_input)

    def hide_macronutrient_fields(self):
        # Remove os campos de macronutrientes se não for "Alimentos"
        if self.protein_input:
            self.remove_widget(self.protein_input)
            self.protein_input = None
        if self.carb_input:
            self.remove_widget(self.carb_input)
            self.carb_input = None

    def save_item(self, instance):
        name = self.item_name_input.text
        quantity = float(self.item_quantity_input.text) if self.category_spinner.text == 'Alimentos' else int(self.item_quantity_input.text)
        category = self.category_spinner.text

        # Se a categoria for "Alimentos", salva também os macronutrientes
        if category == 'Alimentos':
            proteins = float(self.protein_input.text) if self.protein_input else 0
            carbohydrates = float(self.carb_input.text) if self.carb_input else 0
            new_item = {'name': name, 'quantity': quantity, 'category': category, 'proteins': proteins, 'carbohydrates': carbohydrates}
        else:
            new_item = {'name': name, 'quantity': quantity, 'category': category}

        if self.item:
            # Atualizar item existente
            self.item.update(new_item)
        else:
            # Adicionar novo item
            stock_data.append(new_item)

        self.main_screen.update_stock_list()
        self.show_popup(f"Item '{name}' salvo com sucesso!")
        self.main_screen.go_to_main_screen()

    def cancel(self, instance):
        self.main_screen.go_to_main_screen()

    def show_popup(self, message):
        popup = Popup(title="Status", content=Label(text=message), size_hint=(0.6, 0.4))
        popup.open()

# Tela principal que exibe os itens do estoque
class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [10, 10, 10, 10]  # Padding para tornar a interface mais espaçosa

        # Título
        self.add_widget(Label(text="Estoque", size_hint=(1, 0.1), font_size=32))

        # Área de scroll para os itens do estoque
        self.stock_list_layout = GridLayout(cols=1, size_hint_y=None, padding=[0, 10], spacing=10)
        self.stock_list_layout.bind(minimum_height=self.stock_list_layout.setter('height'))

        scroll_view = ScrollView(size_hint=(1, 0.8))
        scroll_view.add_widget(self.stock_list_layout)
        self.add_widget(scroll_view)

        # Botão para adicionar novo item
        add_button = Button(text="Adicionar Item", size_hint=(1, 0.1), background_color=(0.2, 0.6, 1, 1))
        add_button.bind(on_press=self.add_item)
        self.add_widget(add_button)

        self.update_stock_list()

    def update_stock_list(self):
        # Limpa a lista atual e a preenche com os itens do estoque agrupados por categoria
        self.stock_list_layout.clear_widgets()

        categorized_items = {}
        for item in stock_data:
            if item['category'] not in categorized_items:
                categorized_items[item['category']] = []
            categorized_items[item['category']].append(item)

        # Exibir categorias e itens
        for category, items in categorized_items.items():
            # Exibir a categoria
            category_label = Label(text=category, size_hint_y=None, height=40, font_size=24, color=(0, 0, 1, 1))
            self.stock_list_layout.add_widget(category_label)

            # Exibir os itens da categoria
            for item in items:
                if category == 'Alimentos':
                    item_label = Label(text=f"{item['name']} - {item['quantity']} kg, Proteínas: {item['proteins']}g, Carboidratos: {item['carbohydrates']}g", size_hint_y=None, height=40)
                else:
                    item_label = Label(text=f"{item['name']} - {item['quantity']} unidades", size_hint_y=None, height=40)

                edit_button = Button(text="Editar", size_hint_y=None, height=40, background_color=(0.6, 0.8, 0.2, 1))
                delete_button = Button(text="Remover", size_hint_y=None, height=40, background_color=(1, 0.2, 0.2, 1))

                item_box = BoxLayout(size_hint_y=None, height=40)
                item_box.add_widget(item_label)
                item_box.add_widget(edit_button)
                item_box.add_widget(delete_button)

                # Função para editar
                edit_button.bind(on_press=lambda btn, i=item: self.edit_item(i))

                # Função para remover
                delete_button.bind(on_press=lambda btn, i=item: self.remove_item(i))

                self.stock_list_layout.add_widget(item_box)

    def add_item(self, instance):
        self.clear_widgets()
        self.add_widget(StockItemScreen(self))

    def edit_item(self, item):
        self.clear_widgets()
        self.add_widget(StockItemScreen(self, item=item))

    def remove_item(self, item):
        stock_data.remove(item)
        self.update_stock_list()

    def go_to_main_screen(self):
        self.clear_widgets()
        self.__init__()

# Aplicativo principal
class StockApp(App):
    def build(self):
        return MainScreen()

if __name__ == "__main__":
    StockApp().run()

                