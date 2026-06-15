import logging
from typing import Dict, Any, Optional
from agents.base import BaseAgent

logger = logging.getLogger(__name__)

DOC_AI_SYSTEM_PROMPT = """You are the Document AI Agent for FreightGPT UAE.
Process: POD (Proof of Delivery), BOL (Bill of Lading), Invoices, Contracts, Customs Documents.
Workflow: Upload PDF -> OCR -> AI Extraction -> Database Entry.
Extract structured data from logistics documents with high accuracy.
Handle Arabic, English, and bilingual documents common in GCC logistics."""


class DocumentAIAgent(BaseAgent):
    def __init__(self, model: str = "gpt-4"):
        super().__init__("document_ai", model)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "process_document")
        doc_type = input_data.get("document_type", "pod")
        ocr_text = input_data.get("ocr_text", "")
        file_metadata = input_data.get("file_metadata", {})

        if action == "process_document":
            return await self._process_document(doc_type, ocr_text, file_metadata)
        elif action == "extract_pod":
            return await self._extract_pod(ocr_text, file_metadata)
        elif action == "extract_bol":
            return await self._extract_bol(ocr_text, file_metadata)
        elif action == "extract_invoice":
            return await self._extract_invoice(ocr_text, file_metadata)
        elif action == "extract_contract":
            return await self._extract_contract(ocr_text, file_metadata)
        elif action == "validate_document":
            return await self._validate_document(ocr_text, doc_type)
        else:
            return await self._process_document(doc_type, ocr_text, file_metadata)

    async def _process_document(self, doc_type: str, ocr_text: str,
                                metadata: Dict[str, Any]) -> Dict[str, Any]:
        extraction_methods = {
            "pod": self._extract_pod,
            "bol": self._extract_bol,
            "invoice": self._extract_invoice,
            "contract": self._extract_contract,
            "customs": self._extract_customs,
        }
        extractor = extraction_methods.get(doc_type, self._extract_generic)
        extraction = await extractor(ocr_text, metadata)
        validation = await self._validate_document(ocr_text, doc_type)
        return {
            "document_type": doc_type,
            "extraction": extraction,
            "validation": validation,
            "status": "processed",
        }

    async def _extract_pod(self, ocr_text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Extract Proof of Delivery data from this OCR text:
OCR Text: {ocr_text}
Metadata: {metadata}

Extract: delivery_date, recipient_name, signature_present (yes/no), delivery_status,
received_items, damage_notes, pod_reference_number, delivery_location, timestamp.
Handle Arabic text if present."""
        result = await self.think(prompt, DOC_AI_SYSTEM_PROMPT)
        return {"pod_data": result}

    async def _extract_bol(self, ocr_text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Extract Bill of Lading data from this OCR text:
OCR Text: {ocr_text}
Metadata: {metadata}

Extract: bol_number, shipper_name, consignee_name, carrier_name, origin_port,
destination_port, vessel_name (if ocean), container_numbers, seal_numbers,
commodity_description, weight, volume, piece_count, shipping_terms, date_issued."""
        result = await self.think(prompt, DOC_AI_SYSTEM_PROMPT)
        return {"bol_data": result}

    async def _extract_invoice(self, ocr_text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Extract Invoice data from this OCR text:
OCR Text: {ocr_text}
Metadata: {metadata}

Extract: invoice_number, invoice_date, due_date, vendor_name, customer_name,
line_items (description, quantity, unit_price, total), subtotal, tax_amount,
total_amount, currency, payment_terms, vat_number (TRN for UAE).
Handle Arabic/English bilingual invoices."""
        result = await self.think(prompt, DOC_AI_SYSTEM_PROMPT)
        return {"invoice_data": result}

    async def _extract_contract(self, ocr_text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Extract Contract data from this OCR text:
OCR Text: {ocr_text}
Metadata: {metadata}

Extract: contract_number, parties_involved, effective_date, expiry_date,
service_terms, payment_terms, termination_clauses, liability_limits,
renewal_terms, applicable_law (especially relevant for GCC jurisdictions)."""
        result = await self.think(prompt, DOC_AI_SYSTEM_PROMPT)
        return {"contract_data": result}

    async def _extract_customs(self, ocr_text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Extract Customs Document data from this OCR text:
OCR Text: {ocr_text}
Metadata: {metadata}

Extract: customs_declaration_number, hs_codes, goods_description, origin_country,
destination_country, declared_value, duties_paid, customs_broker, clearance_status.
Focus on GCC customs procedures (UAE, Saudi, Qatar, Oman, Bahrain)."""
        result = await self.think(prompt, DOC_AI_SYSTEM_PROMPT)
        return {"customs_data": result}

    async def _extract_generic(self, ocr_text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Extract all relevant information from this document:
OCR Text: {ocr_text}
Metadata: {metadata}

Identify document type, then extract all key fields, dates, names, amounts, reference numbers."""
        result = await self.think(prompt, DOC_AI_SYSTEM_PROMPT)
        return {"generic_extraction": result}

    async def _validate_document(self, ocr_text: str, doc_type: str) -> Dict[str, Any]:
        prompt = f"""Validate this {doc_type.upper()} document:
OCR Text: {ocr_text}

Check: completeness of required fields, data consistency, signature presence (for POD),
date validity, amount calculations (for invoices), potential fraud indicators.
Return: validation_status (valid/invalid/needs_review), issues_found, confidence_score."""
        result = await self.think(prompt, DOC_AI_SYSTEM_PROMPT)
        return {"validation": result}
