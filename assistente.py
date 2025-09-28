import pyttsx3
import comtypes
import speech_recognition as sr # SpeechRecognition e PyAudio (usado internamente): Ferramentas open-source para capturar áudio de dispositivos.
import os
from dotenv import load_dotenv
from groq import Groq # groq: Cliente Python para interagir com a API da Groq, que fornece acesso a modelos de linguagem (LLMs).
import soundcard as sc
import numpy as np

load_dotenv()

# Groq
try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    print(f"Erro ao inicializar o cliente Groq: {e}\nVerifique sua GROQ_API_KEY no arquivo .env")
    exit()

# A primeira mensagem com "role": "system" define os objetivos do assistente.
historico_conversa = [
    {
        "role": "system",
        "content": "Você é um entrevistador de emprego amigável e profissional. Seu nome é Sidekick. Você está conduzindo uma entrevista para uma vaga de desenvolvedor Python. Comece a entrevista se apresentando e fazendo a primeira pergunta. Faça uma pergunta por vez e espere a resposta do candidato. Mantenha suas respostas e perguntas concisas."
    }
]

# Tenta encontrar o índice de um dispositivo de áudio virtual (Principal (FIX))
def encontrar_cabo_virtual():
    PALAVRAS_CHAVE_CABO_VIRTUAL = ["cable", "blackhole"]
    try:
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            nome_dispositivo_lower = name.lower()
            if any(palavra in nome_dispositivo_lower for palavra in PALAVRAS_CHAVE_CABO_VIRTUAL):
                print(f"Dispositivo principal: Cabo de áudio virtual encontrado no índice {index}: '{name}'")
                return index
    except Exception as e:
        print(f"Ocorreu um erro ao procurar por cabo virtual: {e}")
    return None

def falar_texto(texto):
    # Desafio: A biblioteca pyttsx3 pode falhar em produzir som após a primeira chamada.
    # Solução: O motor e a interface COM são inicializados
    try:
        # Inicializa a interface COM para esta thread específica.
        comtypes.CoInitializeEx(comtypes.COINIT_APARTMENTTHREADED)
        # Cria uma nova instância do motor de voz.
        engine = pyttsx3.init()
        print(f"Sidekick: {texto}")
        engine.say(texto)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"Ocorreu um erro crítico ao tentar falar: {e}")

def transcrever_audio(audio_data, reconhecedor):
    # Desafio: Substituir a transcrição via API por uma solução local.
    # Solução: Utiliza "recognize_whisper", que executa o modelo da OpenAI localmente.
    try:
        texto = reconhecedor.recognize_whisper(audio_data, model="base", language="portuguese").lower()
        print(f"Candidato: {texto}")
        return texto
    except sr.UnknownValueError:
        return None
    except Exception as e:
        print(f"Erro na transcrição: {e}")
        return None

# Envia o texto transcrito para o LLM através da API da Groq e obtém resposta.
def obter_resposta_ia(texto_usuario):
    global historico_conversa
    historico_conversa.append({"role": "user", "content": texto_usuario})

    try:
        chat_completion = client.chat.completions.create(
            messages=historico_conversa,
            # Versão Llama suportada
            model="meta-llama/llama-4-scout-17b-16e-instruct",
        )
        resposta = chat_completion.choices[0].message.content
        historico_conversa.append({"role": "assistant", "content": resposta})
        return resposta
    except Exception as e:
        print(f"Ocorreu um erro ao chamar a API da Groq: {e}")
        return "Desculpe, estou com um problema de conexão no momento."

# Usa a IA para gerar um resumo da conversa e salva o resultado em um arquivo.
def gerar_resumo():
    # Desafio: Cumprir o requisito de gerar transcrição e resumo.
    # Solução: Reutiliza a função de chamada da IA, com um "prompt" diferente, instruindo a agir como um assistente de RH e analisar a conversa em vez de participar dela.
    print("\n\n Gerando Resumo da Entrevista ")
    prompt_resumo = {
        "role": "system",
        "content": "Você é um assistente de RH. Analise a transcrição da entrevista a seguir e forneça um resumo conciso dos pontos principais. Destaque as habilidades, experiências e a adequação do candidato para a vaga de desenvolvedor Python."
    }
    historico_para_resumo = [prompt_resumo] + historico_conversa
    
    try:
        chat_completion = client.chat.completions.create(
            messages=historico_para_resumo,
            model="meta-llama/llama-4-scout-17b-16e-instruct",
        )
        resumo = chat_completion.choices[0].message.content
        print(f"\nResumo da Entrevista:\n{resumo}")
        
        with open("resumo_entrevista.txt", "w", encoding="utf-8") as f:
            f.write(" Transcrição Completa \n")
            for item in historico_conversa[1:]:
                role = "Entrevistador" if item['role'] == 'assistant' else "Candidato"
                f.write(f"{role}: {item['content']}\n")
            f.write("\n\n Resumo Gerado pela IA \n")
            f.write(resumo)
        print("\nTranscrição e resumo salvos em 'resumo_entrevista.txt'")

    except Exception as e:
        print(f"Ocorreu um erro ao gerar o resumo: {e}")

# Modo para escolher entre teste/entrevista
def selecionar_modo_execucao():
    print("Por favor, selecione o modo de execução:")
    print("1. Modo Entrevista Ao Vivo (Ouve o áudio da chamada - Zoom/Meet)")
    print("2. Modo de Teste/Desenvolvimento (Ouve o seu microfone padrão)")
    while True:
        escolha = input("Digite 1 ou 2 e pressione Enter: ")
        if escolha in ['1', '2']:
            return escolha
        else:
            print("Escolha inválida. Por favor, digite 1 ou 2.")

# Configura os dispositivos, inicia a conversa e gerencia o loop de interação.
# FIX: alternagem de fallback
def main():
    modo = selecionar_modo_execucao()
    reconhecedor = sr.Recognizer()
    metodo_captura = None
    dispositivo_loopback_speaker = None
    indice_cabo_virtual = None

    if modo == '1': # Modo ao vivo
        print("\nModo entrevista ativado.")
        
        # Tenta usar o cabo de áudio virtual primeiro.
        print("Captura de áudio: Tentando Cabo de Áudio Virtual (Principal)")
        indice_cabo_virtual = encontrar_cabo_virtual()
        
        if indice_cabo_virtual is not None:
            metodo_captura = "cabo_virtual"
        else:
            # FALLBACK: Se o cabo virtual não for encontrado, tenta usar o loopback do soundcard.
            print("Aviso: Cabo de áudio virtual não encontrado.")
            print("Tentando método alternativo (Fallback): Loopback de áudio do sistema (soundcard).")
            try:
                dispositivo_loopback_speaker = sc.default_speaker()
                print(f"Sucesso! Usando fallback via soundcard: '{dispositivo_loopback_speaker.name}'")
                metodo_captura = "loopback"
            except Exception as e:
                # Se ambos os métodos falharem, exibe o erro final.
                print(f"\nERRO: O método de captura Loopback (fallback) também falhou. ({e})")
                print("Nenhum método de captura de áudio funcional foi encontrado.")
                print("Soluções possíveis:")
                print("(Recomendado) Instale um cabo de áudio virtual (ex: VB-CABLE para Windows, BlackHole para macOS).")
                print("Verifique se seus drivers de áudio estão funcionando corretamente.")
                exit()

    elif modo == '2': # modo de teste
        print("\nModo teste ativado")
        print("Ouvindo o microfone padrão do sistema.")
        metodo_captura = "microfone_padrao"

    # Inicio da entrevista
    print("\nAssistente pronto. Iniciando a conversa...")
    resposta_inicial_ia = obter_resposta_ia("Comece a entrevista se apresentando e fazendo a primeira pergunta.")
    falar_texto(resposta_inicial_ia)

    # Loop da conversa
    while True:
        try:
            texto_transcrito = None
            
            if metodo_captura == "loopback":
                print("\nOuvindo via Loopback (Fallback)... Fale na chamada durante os próximos 7 segundos.")
                with sc.get_microphone(id=str(dispositivo_loopback_speaker.id), include_loopback=True).recorder(samplerate=16000) as gravador:
                    dados_gravados = gravador.record(numframes=16000 * 7)
                if dados_gravados.size > 0 and np.max(np.abs(dados_gravados)) > 0.01:
                    print("Gravação concluída, transcrevendo...")
                    audio_normalizado = dados_gravados * 32767
                    audio_bytes = audio_normalizado.astype(np.int16).tobytes()
                    audio_data = sr.AudioData(audio_bytes, sample_rate=16000, sample_width=2)
                    texto_transcrito = transcrever_audio(audio_data, reconhecedor)
                else:
                    print("Silêncio detectado durante o período de gravação.")
            
            elif metodo_captura in ["cabo_virtual", "microfone_padrao"]:
                source = sr.Microphone() if metodo_captura == "microfone_padrao" else sr.Microphone(device_index=indice_cabo_virtual)
                prompt = "\nOuvindo seu microfone... Fale agora." if metodo_captura == "microfone_padrao" else "\nOuvindo via Cabo Virtual (Principal)... Fale na chamada."
                print(prompt)
                with source as s:
                    reconhecedor.adjust_for_ambient_noise(s, duration=1)
                    try:
                        audio = reconhecedor.listen(s, timeout=7, phrase_time_limit=15)
                        texto_transcrito = transcrever_audio(audio, reconhecedor)
                    except sr.WaitTimeoutError:
                        print("Silêncio detectado.")

            # Processamento da fala
            if texto_transcrito:
                if "entrevista" in texto_transcrito and ("encerrar" in texto_transcrito or "cerrar" in texto_transcrito or "serrar" in texto_transcrito):
                    falar_texto("Entendido. Encerrando a sessão e gerando o resumo.")
                    break
                
                resposta_ia = obter_resposta_ia(texto_transcrito)
                falar_texto(resposta_ia)

        except Exception as e:
            print(f"Ocorreu um erro no loop principal: {e}")
            break
            
    # Após o fim do loop, gera o resumo da entrevista.
    gerar_resumo()

if __name__ == "__main__":
    main()