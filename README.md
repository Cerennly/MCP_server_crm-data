🚀 MCP Server – CRM Data

Bu proje, CRM (Customer Relationship Management) verilerini AI asistanlarına (ör. Claude Desktop) güvenli, yapılandırılmış ve standart bir şekilde sunmak için geliştirilmiş bir Model Context Protocol (MCP) Server uygulamasıdır.

Amaç:
AI sistemlerinin müşteri verilerine kontrollü, güvenli ve anlamlı erişim sağlamasını mümkün kılmak.

🎯 Projenin Amacı

Modern AI asistanları, doğru bağlam (context) ile çok daha güçlü çalışır.
Bu MCP Server:

CRM verilerini standartlaştırır

AI sistemlerine okunabilir formatta sunar

Yetkilendirme katmanı ile veri güvenliğini sağlar

Claude Desktop gibi MCP uyumlu uygulamalarla entegre çalışır

✨ Özellikler
🔎 Veri Erişimi

Müşteri bilgileri

Satış fırsatları (deals / opportunities)

İletişim geçmişi

⚡ Gelişmiş Sorgulama

Filtreleme

Arama

Büyük veri setlerinde performanslı sorgular

🔐 Güvenli Entegrasyon

Yetkilendirme katmanı

Hassas müşteri verisi koruması

Kontrollü veri paylaşımı

🤖 Claude Desktop Uyumluluğu

MCP standardı sayesinde doğrudan entegrasyon

AI destekli CRM sorgulama imkanı

🛠️ Kullanılan Teknolojiler
Katman	Teknoloji
Dil	Python / TypeScript
Protokol	Model Context Protocol (MCP SDK)
Veri Kaynağı	SQLite / PostgreSQL / CRM API (Salesforce, Hubspot vb.)
Test Aracı	MCP Inspector
📦 Kurulum
Gereksinimler

Python 3.10+
veya

Node.js 18+

Ayrıca test için:

MCP Inspector

1️⃣ Repository’yi Klonla
git clone https://github.com/Cerennly/MCP_server_crm-data.git
cd MCP_server_crm-data

2️⃣ Bağımlılıkları Yükle

Python için:

pip install -r requirements.txt


veya Node.js için:

npm install

3️⃣ Sunucuyu Başlat
python main.py


veya

npm start

🧠 Mimari Yaklaşım

Bu proje şu prensiplere dayanır:

🔹 Context-first design

🔹 Secure data exposure

🔹 Protocol-driven architecture

🔹 AI-ready CRM integration

🔒 Güvenlik Notu

Bu sunucu, hassas müşteri verilerini expose ettiği için:

Production ortamında kimlik doğrulama eklenmelidir

API key veya token bazlı erişim kullanılmalıdır

Environment variable yönetimi önerilir

📌 Kullanım Senaryosu

Örnek kullanım:

"Son 30 gün içinde kapanan satışları getir."
"ABC şirketine ait müşteri geçmişini özetle."
"Pipeline'daki açık fırsatları listele."

AI asistanı bu soruları MCP Server üzerinden CRM verisini kullanarak yanıtlayabilir.

📈 Gelecek Geliştirmeler

Role-based access control

Loglama ve audit mekanizması

Çoklu CRM entegrasyonu

Docker desteği

Cloud deployment

👩‍💻 Author

Ceren
AI + Data + CRM Systems Engineering
