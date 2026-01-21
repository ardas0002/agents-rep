# Cold Emails Agent

Agent do automatycznego generowania i wysyłania zimnych emaili sprzedażowych.

## Wymagania

- Python 3.12+
- Konto SendGrid z API key
- Zmienna środowiskowa `OPENAI_API_KEY`
- Zmienna środowiskowa `SENDGRID_API_KEY`

## Instalacja

### 1. Utwórz wirtualne środowisko

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Zainstaluj zależności

```bash
pip install -r requirements.txt
```

### 3. Skonfiguruj zmienne środowiskowe

Utwórz plik `.env` w katalogu `1_foundations/agents/cold-emails-agent/` z następującą zawartością:

```env
OPENAI_API_KEY=your_openai_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
```

### 4. Edytuj adresy email w `main.py`

Przed uruchomieniem, zaktualizuj adresy email w funkcji `send_html_email`:
- `from_email` - Twój zweryfikowany adres w SendGrid
- `to_email` - Adres odbiorcy

## Uruchomienie

```bash
python main.py
```

## Jak to działa

Agent składa się z:
1. **Trzech agentów sprzedażowych** - generują różne wersje emaili (profesjonalny, zabawny, zwięzły)
2. **Sales Manager** - wybiera najlepszy email i przekazuje go dalej
3. **Email Manager** - formatuje email do HTML i wysyła go

Agent automatycznie:
- Generuje 3 różne wersje emaila
- Wybiera najlepszą wersję
- Tworzy temat emaila
- Konwertuje treść do HTML
- Wysyła email przez SendGrid

