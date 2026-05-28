from app.schemas import PrecatorioInput


REQUIRED_FIELDS = (
    "numero_processo",
    "ente_devedor",
    "valor_estimado",
    "nome_credor",
    "natureza",
    "status_documental",
)


def is_field_filled(data: PrecatorioInput, field_name: str) -> bool:
    value = getattr(data, field_name)

    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, int | float):
        return value > 0

    return True


def validate_required_fields(data: PrecatorioInput) -> list[str]:
    return [field_name for field_name in REQUIRED_FIELDS if not is_field_filled(data, field_name)]
