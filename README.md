# FLITERING APP

Aplikasaun web **Inventory** (jestaun stok) ne'ebé dezenvolve ho **Django**, ho funsionalidade prinsipal **filtra** no buka item inventory tuir kategoria, status stok, no seluk tan.

> ⚠️ Naran "Flitering" mak nu'udar naran projetu. Bele troka ba "Filtering App" se presiza.

---

## 📌 Deskrisaun

FLITERING APP ajuda utilizadór atu kontrola no jere item iha inventory: rejistu item foun, atualiza kuantidade stok, no filtra item ho lais tuir kondisaun ne'ebé presiza (ezemplu: item ne'ebé stok badak ka remata).

## ✨ Funsionalidade

- Hatama, edita, no hamoos item inventory (CRUD)
- Filtra item tuir **kategoria**, **status stok**, no **data**
- Buka (*search*) item tuir naran ka kódigu
- Hatudu total item, total stok, no alerta ba stok badak
- Rejistu stok tama (*in*) no sai (*out*)
- Esporta lista ba CSV *(opsionál)*
- Painel admin Django atu jere dadus

## 🏷️ Status Stok

| Kondisaun | Status |
|-----------|--------|
| Kuantidade > limite mínimu | Disponivel |
| Kuantidade ≤ limite mínimu | Stok Badak |
| Kuantidade = 0 | Remata |

> Troka tabela ne'e tuir regra loloos ne'ebé aplikasaun uza.

## 🛠️ Teknolojia

| Parte | Ferramenta |
|-------|-----------|
| Backend | Python 3, Django |
| Database | SQLite (default) / MySQL / PostgreSQL |
| Frontend | HTML, CSS, Bootstrap |
| Seluk | django-filter *(opsionál, ba filtru)* |

## 📁 Estrutura Projetu

```
flitering-app/
├── manage.py
├── requirements.txt
├── README.md
├── flitering_app/        # konfigurasaun projetu (settings, urls)
├── inventory/            # app prinsipal
│   ├── models.py
│   ├── views.py
│   ├── filters.py
│   ├── urls.py
│   └── templates/
└── static/               # CSS, JS, imajen
```

## 🚀 Instalasaun

### 1. Klone repozitóriu

```bash
git clone https://github.com/<username>/flitering-app.git
cd flitering-app
```

### 2. Kria virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Instala dependénsia

```bash
pip install -r requirements.txt
```

### 4. Halo migrasaun database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Kria superuser (admin)

```bash
python manage.py createsuperuser
```

### 6. Funsiona servidór

```bash
python manage.py runserver
```

Loke browser no bá ba: **http://127.0.0.1:8000/**

## 📖 Oinsá Uza

1. Login ba painel admin iha `/admin` (se presiza).
2. Hatama kategoria no item inventory.
3. Uza formuláriu filtru iha pájina lista item atu hili kategoria ka status stok.
4. Rejistu stok tama/sai atu atualiza kuantidade.

## 🗄️ Modelu Database (sugestaun)

**Category**

| Field | Tipu | Deskrisaun |
|-------|------|-----------|
| id | Integer (PK) | ID úniku |
| naran | CharField | Naran kategoria |

**Item**

| Field | Tipu | Deskrisaun |
|-------|------|-----------|
| id | Integer (PK) | ID úniku |
| kodigu | CharField | Kódigu item |
| naran | CharField | Naran item |
| kategoria | ForeignKey | Liga ba Category |
| kuantidade | Integer | Stok atual |
| limite_minimu | Integer | Limite alerta stok badak |
| created_at | DateTime | Data rejistu |

**StockMovement**

| Field | Tipu | Deskrisaun |
|-------|------|-----------|
| id | Integer (PK) | ID úniku |
| item | ForeignKey | Liga ba Item |
| tipu | CharField | `tama` ka `sai` |
| kuantidade | Integer | Kuantidade movimentu |
| data | DateTime | Data movimentu |

## 🔮 Dezenvolvimentu Futuru

- Autentikasaun utilizadór ho nivel asesu
- Dashboard ho gráfiku estatístika
- Esporta ba Excel/PDF
- Skan barcode/QR code

## 👤 Autór

**Rivaldo**
Estudante Engenharia Informatika, Universidade Nacional Timor Lorosa'e (UNTL)
Timor-Leste

## 📄 Lisensa

Projetu ida-ne'e uza lisensa **MIT**. *(Troka se presiza.)*
