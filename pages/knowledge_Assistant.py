from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class KnowledgeAssistant(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.question = page.get_by_test_id("question")
        self.ask_button = page.get_by_test_id("ask")
        self.answer = page.get_by_test_id("answer")
        self.region_dropdown = page.get_by_test_id("region")
        self.role_dropdown = page.get_by_test_id("role")
        self.citations = page.get_by_test_id("citation")
        self.visible_documents = page.get_by_test_id("docs")


    def select_region(self, region: str):
        self.region_dropdown.select_option(label=region)
        self.page.wait_for_load_state("networkidle")

    def get_selected_region(self):
        return self.region_dropdown.input_value()

    def select_role(self, role: str):
        self.role_dropdown.select_option(label=role)
        self.page.wait_for_load_state("networkidle")

    def get_selected_role(self):
        return self.role_dropdown.input_value()

    def ask_question(self, question: str):
        self.question.fill(question)
        self.ask_button.click()
        self.answer.wait_for(state="visible")
        self.page.wait_for_load_state("networkidle")

    def get_answer(self) -> str:
        expect(self.answer).not_to_contain_text(
            "Thinking...",
            timeout=30000
        )
        return self.answer.inner_text()

    def get_citations(self):
        if self.citations.count() > 0:
            expect(self.citations.first).to_be_visible(timeout=10000)
        return [citation.inner_text() for citation in self.citations.all()]

    def get_visible_documents(self):
        if self.visible_documents.count() > 0:
            expect(self.visible_documents.first).to_be_visible(timeout=10000)
        documents = [doc.inner_text() for doc in self.visible_documents.all()]

        print("\n---- VISIBLE DOCUMENTS ----")
        for doc in documents:
            print(doc)
        print("-----------------------------\n")

        return documents

    def get_results(self):
        return {
            "answer": self.get_answer(),
            "citations": self.get_citations(),
            "visible_documents": self.get_visible_documents()
        }