import requests
from textblob import TextBlob

def buscar_ongs_no_google():
    api_key = 'YOUR_GOOGLE_API_KEY'
    cse_id = 'YOUR_CUSTOM_SEARCH_ENGINE_ID'
    
    query = 'ONGs no Rio Grande do Sul site:br'
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}'
    
    response = requests.get(url)
    results = response.json().get('items', [])
    
    print("Resultados da busca no Google:")
    print(results)  # Exibe os resultados da busca
    
    return results

def obter_avaliacoes_google(place_id):
    api_key = 'YOUR_GOOGLE_API_KEY'
    url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}'
    
    response = requests.get(url)
    data = response.json()
    reviews = data.get('result', {}).get('reviews', [])
    
    print(f"Avaliações para {place_id}:")
    print(reviews)  # Exibe as avaliações
    
    return reviews

def analise_sentimento(texto):
    blob = TextBlob(texto)
    sentiment = blob.sentiment.polarity
    return sentiment

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
    
    ongs_com_avaliacoes = sorted(ongs_com_avaliacoes, key=lambda x: x['avaliacoes_positivas'], reverse=True)
    
    return ongs_com_avaliacoes[:5]

def ongs_menos_visiveis(ongs):
    ongs_menos_visiveis = []
    
    for ong in ongs:
        reviews = obter_avaliacoes_google(ong['place_id'])
        positive_reviews = [review for review in reviews if analise_sentimento(review['text']) > 0]
        
        if positive_reviews and len(positive_reviews) < 5:
            ongs_menos_visiveis.append({
                'nome': ong['nome'],
                'site': ong['site'],
                'avaliacoes_positivas': len(positive_reviews)
            })
    
    return ongs_menos_visiveis

def verificar_avaliacoes_suspeitas(reviews):
    usuarios = {}
    for review in reviews:
        user = review['author_name']
        if user in usuarios:
            usuarios[user] += 1
        else:
            usuarios[user] = 1
    
    suspeitas = [user for user, count in usuarios.items() if count > 2]
    return suspeitas

def buscar_e_analisar_ongs():
    ongs = buscar_ongs_no_google()
    
    if not ongs:
        print("Nenhuma ONG encontrada.")
        return
    
    ongs_classificadas = classificar_ongs_por_avaliacoes(ongs)
    
    if not ongs_classificadas:
        print("Nenhuma ONG com avaliações positivas foi encontrada.")
        return
    
    ongs_com_pouca_visibilidade = ongs_menos_visiveis(ongs)
    
    print("Top 5 ONGs com mais avaliações positivas:")
    for ong in ongs_classificadas:
        print(f"{ong['nome']} - {ong['site']} - Avaliações Positivas: {ong['avaliacoes_positivas']}")
    
    print("\nONGs com avaliações positivas, mas menos visibilidade:")
    for ong in ongs_com_pouca_visibilidade:
        print(f"{ong['nome']} - {ong['site']} - Avaliações Positivas: {ong['avaliacoes_positivas']}")

if __name__ == "__main__":
    buscar_e_analisar_ongs()
