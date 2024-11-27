import requests
from textblob import TextBlob

# Função para buscar ONGs no Google com base em uma consulta personalizada
def buscar_ongs_no_google(query):
    api_key = 'YOUR_GOOGLE_API_KEY'
    cse_id = 'YOUR_CUSTOM_SEARCH_ENGINE_ID'
    
    # Consultando o Google com o critério personalizado do usuário
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}'
    
    response = requests.get(url)
    results = response.json().get('items', [])
    
    print(f"Resultados encontrados para '{query}':")
    for item in results:
        print(f"- {item['title']} | {item['link']}")
    
    return results  # Retorna as ONGs encontradas com links

# Função para obter as avaliações de uma ONG no Google
def obter_avaliacoes_google(place_id):
    api_key = 'YOUR_GOOGLE_API_KEY'
    url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}'
    
    response = requests.get(url)
    data = response.json()
    reviews = data.get('result', {}).get('reviews', [])
    
    return reviews

# Função de análise de sentimento usando TextBlob
def analise_sentimento(texto):
    blob = TextBlob(texto)
    sentiment = blob.sentiment.polarity  # Retorna um valor entre -1 e 1
    return sentiment

# Função para classificar as ONGs por avaliações positivas
def classificar_ongs_por_avaliacoes(ongs):
    ongs_com_avaliacoes = []
    
    for ong in ongs:
        reviews = obter_avaliacoes_google(ong['place_id'])
        positive_reviews = [review for review in reviews if analise_sentimento(review['text']) > 0]
        
        if positive_reviews:
            ongs_com_avaliacoes.append({
                'nome': ong['nome'],
                'site': ong['site'],
                'avaliacoes_positivas': len(positive_reviews)
            })
    
    # Ordenando as ONGs por avaliações positivas
    ongs_com_avaliacoes = sorted(ongs_com_avaliacoes, key=lambda x: x['avaliacoes_positivas'], reverse=True)
    
    return ongs_com_avaliacoes[:5]  # Retorna as 5 ONGs com mais avaliações positivas

# Função para identificar ONGs com menos visibilidade
def ongs_menos_visiveis(ongs):
    ongs_menos_visiveis = []
    
    for ong in ongs:
        reviews = obter_avaliacoes_google(ong['place_id'])
        positive_reviews = [review for review in reviews if analise_sentimento(review['text']) > 0]
        
        if positive_reviews and len(positive_reviews) < 5:  # Se tem poucas avaliações positivas
            ongs_menos_visiveis.append({
                'nome': ong['nome'],
                'site': ong['site'],
                'avaliacoes_positivas': len(positive_reviews)
            })
    
    return ongs_menos_visiveis

# Função para buscar e analisar as ONGs com base na consulta personalizada
def buscar_e_analisar_ongs():
    # Solicitar ao usuário a consulta personalizada
    query = input("Digite o que deseja procurar (ex: 'ONGs ambientais no Rio Grande do Sul'): ")
    
    # Busca as ONGs no Google com a consulta personalizada
    ongs = buscar_ongs_no_google(query)
    
    if not ongs:
        print("Nenhuma ONG encontrada com esse critério.")
        return
    
    # Classificar as ONGs por avaliações positivas
    ongs_classificadas = classificar_ongs_por_avaliacoes(ongs)
    
    if not ongs_classificadas:
        print("Nenhuma ONG com avaliações positivas foi encontrada.")
        return
    
    # Identificar ONGs com avaliações positivas, mas com menor visibilidade
    ongs_com_pouca_visibilidade = ongs_menos_visiveis(ongs)
    
    # Exibir os resultados
    print("\nTop 5 ONGs com mais avaliações positivas:")
    for ong in ongs_classificadas:
        print(f"{ong['nome']} - {ong['site']} - Avaliações Positivas: {ong['avaliacoes_positivas']}")
    
    print("\nONGs com avaliações positivas, mas menos visibilidade:")
    for ong in ongs_com_pouca_visibilidade:
        print(f"{ong['nome']} - {ong['site']} - Avaliações Positivas: {ong['avaliacoes_positivas']}")

if __name__ == "__main__":
    buscar_e_analisar_ongs()
