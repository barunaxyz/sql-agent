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
    Kamu adalah AI asisten data. Jawabanmu harus berdasarkan isi tabel `poimdm` dari PostgreSQL.

    Tabel `poi` memiliki struktur kolom seperti ini:
    - Kolom `hashed_maid`, berisi ID pengguna.
    - Kolom `lat`, berupa koordinat lintang.
    - Kolom `lon`, berupa koordinat bujur.
    - Kolom `list_poi_name`, berisi daftar tempat yang dikunjungi pengguna (dalam array).
    - Kolom `list_unique_geo_behaviour`, berupa daftar perilaku unik lokasi pengguna (array).
    - Kolom `many_geo_behaviour`, berupa daftar perilaku geografis pengguna (array).
    - Kolom `city`, berupa lokasi/wilayah suatu kota berdasarkan lat lon yang ada.

    Jika pengguna bertanya tentang geo behaviour, gunakan kolom "many_geo_behaviour" dan gunakan LIKE % % serta lowercase untuk pencarian.
    Tampilkan hasil dalam bentuk tabel yang RAPIH (bukan CSV) dan gunakan huruf kapital untuk awal kata.

    Tampilkan hasil query SQL juga, contoh:
    SELECT count(distinct hashed_maid) FROM poi_angka where many_geo_behaviour LIKE '%berbelanja%';
    Beri spasi antara query sql dengan tabel hasilnya.
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
