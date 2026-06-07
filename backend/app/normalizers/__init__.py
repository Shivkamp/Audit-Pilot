from app.core.constants import (
    DOCUMENT_TYPE_FORM_26AS,
    DOCUMENT_TYPE_INVOICE,
    DOCUMENT_TYPE_TDS_CHALLAN,
    DOCUMENT_TYPE_TDS_WORKING,
    DOCUMENT_TYPE_VENDOR_LEDGER,
    DOCUMENT_TYPE_VENDOR_MASTER,
)
from app.normalizers.base import BaseNormalizer, NormalizedItem
from app.normalizers.form26as_normalizer import Form26ASNormalizer
from app.normalizers.invoice_normalizer import InvoiceNormalizer
from app.normalizers.tds_challan_normalizer import TDSChallanNormalizer
from app.normalizers.tds_working_normalizer import TDSWorkingNormalizer
from app.normalizers.vendor_ledger_normalizer import VendorLedgerNormalizer
from app.normalizers.vendor_master_normalizer import VendorMasterNormalizer

_NORMALIZER_BY_DOCUMENT_TYPE = {
    DOCUMENT_TYPE_VENDOR_MASTER: VendorMasterNormalizer,
    DOCUMENT_TYPE_VENDOR_LEDGER: VendorLedgerNormalizer,
    DOCUMENT_TYPE_TDS_WORKING: TDSWorkingNormalizer,
    DOCUMENT_TYPE_TDS_CHALLAN: TDSChallanNormalizer,
    DOCUMENT_TYPE_FORM_26AS: Form26ASNormalizer,
    DOCUMENT_TYPE_INVOICE: InvoiceNormalizer,
}


def get_normalizer_for_document_type(document_type: str) -> BaseNormalizer | None:
    normalizer_class = _NORMALIZER_BY_DOCUMENT_TYPE.get(document_type)
    if normalizer_class is None:
        return None
    return normalizer_class()


__all__ = [
    "BaseNormalizer",
    "NormalizedItem",
    "Form26ASNormalizer",
    "InvoiceNormalizer",
    "TDSChallanNormalizer",
    "TDSWorkingNormalizer",
    "VendorLedgerNormalizer",
    "VendorMasterNormalizer",
    "get_normalizer_for_document_type",
]