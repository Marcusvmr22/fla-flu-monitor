import os
import time
import requests

from playwright.sync_api import sync_playwright


URL = "https://www.futebolcard.com/information?event=41427"
INTERVALO = 30
DURACAO = 240

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    resposta = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensagem
        },
        timeout=20
    )

    if resposta.ok:
        print("📲 Telegram: alerta enviado com sucesso!")
    else:
        print(f"❌ Erro ao enviar Telegram: {resposta.text}")


def ler_setores(page):
    setores = page.locator("a.match_sector")
    resultado = {}

    for i in range(setores.count()):
        setor = setores.nth(i)

        nome = setor.locator(".match_sector-name").inner_text().strip()
        status = setor.locator(".col-8 p").inner_text().strip()
        preco = setor.locator(".match_sector-price p").inner_text().strip()

        classe = setor.get_attribute("class") or ""
        disponivel = "sold" not in classe

        resultado[nome] = {
            "status": status,
            "preco": preco,
            "disponivel": disponivel
        }

    return resultado


def verificar_mudancas(estado_anterior, estado_atual):
    for nome, dados_atuais in estado_atual.items():

        dados_anteriores = estado_anterior.get(nome)

        if dados_anteriores is None:
            continue

        estava_disponivel = dados_anteriores["disponivel"]
        esta_disponivel = dados_atuais["disponivel"]

        if not estava_disponivel and esta_disponivel:

            print()
            print("🚨 INGRESSO DISPONÍVEL!")
            print(f"🎟️ Setor: {nome}")
            print(f"💰 Preço: {dados_atuais['preco']}")
            print(f"📋 {dados_atuais['status']}")

            mensagem = (
                "🚨 INGRESSO DISPONÍVEL!\n\n"
                "⚽️ Flamengo x Fluminense\n"
                f"📍 Setor: {nome}\n"
                f"💰 Preço: {dados_atuais['preco']}\n"
                f"📋 {dados_atuais['status']}\n\n"
                f"🎟️ {URL}"
            )

            enviar_telegram(mensagem)

        elif estava_disponivel and not esta_disponivel:
            print(f"🔴 {nome} ficou indisponível.")


with sync_playwright() as p:

    print("🌐 Abrindo Chromium...")

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    print("🔎 Abrindo página do Fla x Flu...")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=30000
    )

    print("⏳ Aguardando carregamento inicial...")

    page.wait_for_timeout(5000)

    estado_anterior = ler_setores(page)

    print()
    print("=" * 60)
    print("⚽ MONITOR FLAMENGO x FLUMINENSE")
    print("=" * 60)
    print()

    print("📡 Monitoramento iniciado.")
    print(f"⏱️ Intervalo: {INTERVALO} segundos")
    print(f"⏳ Duração desta execução: {DURACAO} segundos")
    print()

    print("📋 Estado inicial:")
    print()

    for nome, dados in estado_anterior.items():

        if dados["disponivel"]:
            icone = "🟢"
            texto = "DISPONÍVEL"
        else:
            icone = "🔴"
            texto = "INDISPONÍVEL"

        print(
            f"{icone} {texto} | "
            f"{nome} | "
            f"{dados['preco']} | "
            f"{dados['status']}"
        )

    print()
    print("ℹ️ O estado inicial não gera alerta.")
    print("🔎 Aguardando mudanças...")
    print()

    inicio = time.time()

    while time.time() - inicio < DURACAO:

        time.sleep(INTERVALO)

        print("🔄 Atualizando página...")

        try:

            page.reload(
                wait_until="domcontentloaded",
                timeout=30000
            )

            page.wait_for_timeout(3000)

            estado_atual = ler_setores(page)

            verificar_mudancas(
                estado_anterior,
                estado_atual
            )

            estado_anterior = estado_atual

            print("✅ Verificação concluída.")
            print()

        except Exception as erro:

            print()
            print("⚠️ Erro durante a atualização:")
            print(erro)
            print("🔁 O monitor continuará tentando.")
            print()

    print("🏁 Execução encerrada.")
    browser.close()
