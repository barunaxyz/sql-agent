from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from config.settings import GOOGLE_API_KEY, DATABASE_URL

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=GOOGLE_API_KEY,
    temperature=0
)

db = SQLDatabase.from_uri(DATABASE_URL)

system_prompt = SystemMessagePromptTemplate.from_template(
    """
    Kamu adalah asisten AI untuk analisis data dari tabel `poimdm` di PostgreSQL.

    Struktur kolom penting:
    - `hashed_maid`: ID pengguna
    - `lat`, `lon`: koordinat
    - `list_poi_name`: daftar tempat yang dikunjungi (string array)
    - `list_unique_geo_behaviour`: daftar perilaku unik (string array)
    - `many_geo_behaviour`: daftar perilaku geografis pengguna, disimpan sebagai string seperti ['job seekers', 'foodies']
    - `city`: kota asal berdasarkan lat-lon

    Kolom seperti `many_geo_behaviour` adalah STRING (bukan array SQL atau JSON). Untuk pencarian perilaku, gunakan:
    ```sql
    WHERE LOWER(many_geo_behaviour) LIKE '%kata%'
    ```

    Jawaban harus:
    - Berdasarkan data di tabel `poimdm`
    - Menyertakan SQL query-nya (beri spasi sebelum hasil)
    - Menampilkan hasil dalam **tabel rapi** (bukan CSV)
    - Menggunakan huruf kapital di awal kata

    Contoh query:
    ```sql
    SELECT COUNT(*) FROM poimdm WHERE LOWER(city) = 'jakarta' AND LOWER(many_geo_behaviour) LIKE '%job seekers%';
    ```

    Jangan parsing array secara manual atau gunakan fungsi kompleks seperti `unnest`, `jsonb_array_elements`, dll kecuali sangat diperlukan.
    """
)



#system_prompt = SystemMessagePromptTemplate.from_template(
#    """
#    Kamu adalah AI asisten data. Kamu hanya boleh menjawab berdasarkan isi tabel `poi` dari database PostgreSQL.
#    Jawabanmu harus dalam format tabel yang rapi (bukan CSV). Jika pengguna bertanya tentang lokasi, gunakan kolom city untuk menentukan daerah berdasarkan koordinat.
#    Jika pengguna bertanya tentang geo behaviour, gunakan kolom many_geo_behaviour dan beri like % % untuk memberikan informasi yang relevan dan menggunakan huruf awal kapital .
#    Tampilkan hasil query sql juga tetapi tidak perlu dibuat tabel tapi rapih, contoh : SELECT hashed_maid, city FROM poi WHERE city = 'Makassar'.
#    """
#)

prompt = ChatPromptTemplate.from_messages([
    system_prompt,
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    prompt=prompt,
    agent_type="tool-calling",
    verbose=True,
    handle_parsing_errors=True
)

def ask_agent(user_input: str, chat_history=[]):
    return agent_executor.invoke({
        "input": user_input,
        "chat_history": chat_history
    })
