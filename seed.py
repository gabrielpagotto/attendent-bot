from sqlmodel import Session
from src.database import create_db_and_tables, engine, Company, Product


def perform_seed():
    create_db_and_tables()

    with Session(engine) as session:
        company = Company(
            name="Rápida Peça Delivery",
            address="Rua dos Motores, 1234, Bairro Auto Center, São Paulo - SP",
            cep="01010-010",
            email="contato@rapidapecadelivery.com",
            phone_number="(11) 4002-5000",
            whatsapp="(11) 98888-7777",
            instagram="rapidapecadelivery",
            cnpj="12.345.678/0001-99",
            opening_hours="Seg a Sex: 8h às 18h, Sáb: 8h às 12h, Dom: Fechado",
        )

        products: list[Product] = []

        products.append(Product(description="Bateria Automotiva Bosch 60Ah", price=450.00, code="BAT-001"))
        products.append(Product(description="Pneu Bridgestone 185/65 R15", price=390.00, code="PNE-002"))
        products.append(Product(description="Velas de Ignição NGK G-Power", price=75.00, code="VEL-003"))
        products.append(Product(description="Filtro de Óleo Fram PH6017A", price=30.00, code="FIL-004"))
        products.append(Product(description="Pastilha de Freio Cobreq Dianteira", price=120.00, code="PAS-005"))
        products.append(Product(description="Disco de Freio Fremax Ventilado", price=230.00, code="DIS-006"))
        products.append(Product(description="Correia Dentada Continental CT1150", price=95.00, code="COR-007"))
        products.append(Product(description="Amortecedor Monroe Dianteiro", price=220.00, code="AMO-008"))
        products.append(Product(description="Óleo de Motor Castrol GTX 15W40 1L", price=42.00, code="OLE-009"))
        products.append(Product(description="Lâmpada Halógena Philips H4", price=35.00, code="LAM-010"))
        products.append(Product(description="Kit de Embreagem Luk Gol G5", price=650.00, code="EMB-011"))
        products.append(Product(description="Parafuso de Rodas Cromado", price=20.00, code="PAR-012"))
        products.append(Product(description="Filtro de Ar Esportivo K&N", price=320.00, code="FIL-013"))
        products.append(Product(description="Radiador Valeo Uno Mille", price=350.00, code="RAD-014"))
        products.append(Product(description="Escapamento Esportivo Inox", price=1200.00, code="ESC-015"))
        products.append(Product(description="Retrovisor Lado Direito Palio 2018", price=180.00, code="RET-016"))
        products.append(Product(description="Sensor de Estacionamento com Display", price=210.00, code="SEN-017"))
        products.append(Product(description="Câmera de Ré Universal", price=150.00, code="CAM-018"))
        products.append(Product(description="Módulo de Ignição Bosch Original", price=350.00, code="MOD-019"))
        products.append(Product(description="Parabarro Dianteiro Hilux 2020", price=250.00, code="BAR-020"))
        products.append(Product(description="Capô Corolla 2015", price=900.00, code="CAP-021"))
        products.append(Product(description="Farol Auxiliar LED Universal", price=280.00, code="FAR-022"))
        products.append(Product(description="Kit Tapete Borracha Universal", price=80.00, code="TAP-023"))
        products.append(Product(description="Rack de Teto Universal Preto", price=350.00, code="RAC-024"))
        products.append(Product(description="Palheta Limpador Traseira Bosch", price=45.00, code="PAL-025"))
        products.append(Product(description="Jogo de Parafusos para Motor", price=60.00, code="JOG-026"))
        products.append(Product(description="Volante Esportivo Universal", price=400.00, code="VOL-027"))
        products.append(
            Product(description="Barra Estabilizadora Dianteira Ranger 2018", price=450.00, code="BAR-028")
        )
        products.append(Product(description="Chave de Roda Cruz Cromada", price=85.00, code="CHA-029"))
        products.append(Product(description="Filtro de Combustível Tecfil", price=35.00, code="FIL-030"))
        products.append(Product(description="Lanterna Traseira Saveiro 2020", price=320.00, code="LAN-031"))
        products.append(Product(description="Kit Suspensão Completo Uno 2017", price=1200.00, code="KIT-032"))
        products.append(Product(description="Coxim do Motor Original", price=200.00, code="COX-033"))
        products.append(Product(description="Paralama Dianteiro Fiesta 2015", price=300.00, code="PAR-034"))
        products.append(Product(description="Lente de Retrovisor Clio", price=60.00, code="LEN-035"))
        products.append(Product(description="Kit Ferramentas Multimarca", price=150.00, code="KIT-036"))
        products.append(Product(description="Terminal de Direção Esquerdo Golf 2015", price=220.00, code="TER-037"))
        products.append(Product(description="Macaco Hidráulico Tipo Jacaré", price=320.00, code="MAC-038"))
        products.append(Product(description="Caixa de Direção Hidráulica", price=1800.00, code="CAI-039"))
        products.append(Product(description="Bomba de Combustível Delphi", price=450.00, code="BOM-040"))
        products.append(Product(description="Espelho Retrovisor Universal", price=75.00, code="ESP-041"))
        products.append(Product(description="Haste Limpador de Para-brisa", price=50.00, code="HAS-042"))
        products.append(Product(description="Buzina Eletrônica Dupla Universal", price=120.00, code="BUZ-043"))
        products.append(Product(description="Protetor de Cárter Corolla 2020", price=250.00, code="PRO-044"))
        products.append(Product(description="Kit Cabo de Velas Bosch", price=120.00, code="CAB-045"))
        products.append(Product(description="Chave Canivete com Transponder", price=350.00, code="CHA-046"))
        products.append(Product(description="Alarme Automotivo Pósitron Universal", price=450.00, code="ALA-047"))
        products.append(Product(description="Cabo de Bateria 3 Metros", price=85.00, code="CAB-048"))
        products.append(Product(description="Aditivo para Radiador Concentrado", price=25.00, code="ADI-049"))
        products.append(Product(description="Protetor Solar para Painel Automotivo", price=60.00, code="PRO-050"))

        session.add(company)
        session.add_all(products)
        session.commit()


if __name__ == "__main__":
    perform_seed()
