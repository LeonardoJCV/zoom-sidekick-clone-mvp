# Sidekick AI - Real-time Interview Assistant (No Recall.ai)

Este projeto apresenta um **assistente de entrevistas em tempo real**, controlado por voz, que escuta o áudio de reuniões (como Zoom ou Google Meet), conduz entrevistas com candidatos a vagas de desenvolvedor Python, e gera um **resumo automatizado da conversa**.

Este projeto utiliza **somente ferramentas open-source** para capturar o áudio da reunião e processá-lo localmente com alta precisão.

⚠️ **Disclaimer:** Este é um MVP funcional e bruto, voltado para validação técnica. Não está pronto para produção e ainda carece de camadas de segurança, privacidade e UX refinada.

---

## ✅ Funcionalidades

- 🎙️ Captura de áudio em tempo real (via loopback ou microfone virtual)
- 🧠 Entrevista conduzida por IA (Groq LLaMA 4)
- 🗣️ Interação por voz com o candidato
- 📝 Transcrição automática com Whisper local
- 📄 Geração de resumo e avaliação do candidato via IA
- 💾 Exporta a conversa e o resumo para arquivo `.txt`

---

## 📦 Pré-requisitos

Certifique-se de ter:

- Python 3.8+
- API Key da [Groq](https://console.groq.com/)
- Dispositivo compatível com:
  - Loopback de áudio (via `soundcard`)
  - OU um cabo de áudio virtual como [VB-CABLE (Windows)](https://vb-audio.com/Cable/) ou [BlackHole (macOS)](https://existential.audio/blackhole/)

---

## ⚙️ Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/sidekick-ai-interview.git
   cd sidekick-ai-interview