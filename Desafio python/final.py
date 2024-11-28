import requests
from textblob import TextBlob

# Substitui para minha chave de API e ID do mecanismo de busca personalizado
API_KEY = 'AIzaSyCAhQgeBcSK-yR3HHnw38reiEma5aStMCo'
CSE_ID = 'e7b03ac1bdaa4410b'

# Função para buscar ONGs no Google com base em uma consulta personalizada
def buscar_ongs_no_google(query):
    """Busca ONGs no Google usando uma consulta personalizada."""
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CSE_ID}'
    response = requests.get(url)
    
    if response.status_code != 200:
        print("⚠️ Erro ao buscar ONGs no Google.")
        return []
    
    results = response.json().get('items', [])
    ongs = []
    
    for item in results:
        ongs.append({
            'nome': item.get('title'),
            'link': item.get('link'),
            'snippet': item.get('snippet', ''),
            'place_id': item.get('pagemap', {}).get('metatags', [{}])[0].get('place:id', '')  # Extrai Place ID
        })
    
    return ongs

# Função para obter avaliações de uma ONG no Google Places API
def obter_avaliacoes_google(place_id):
    """Obtém avaliações de uma ONG com base no Place ID do Google Places API."""
    if not place_id:
        return []
    
    url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={API_KEY}'
    response = requests.get(url)
    
    if response.status_code != 200:
        print("⚠️ Erro ao buscar avaliações no Google Places.")
        return []
    
    data = response.json()
    reviews = data.get('result', {}).get('reviews', [])
    
    return reviews

# Função de análise de sentimento usando TextBlob
def analise_sentimento(texto):
    """Analisa o sentimento do texto usando TextBlob."""
    blob = TextBlob(texto)
    return blob.sentiment.polarity  # Retorna um valor entre -1 (negativo) e 1 (positivo)

# Função para classificar as ONGs por avaliações positivas
def classificar_ongs_por_avaliacoes(ongs):
    """Classifica ONGs com base no número de avaliações positivas."""
    ongs_com_avaliacoes = []
    
    for ong in ongs:
        reviews = obter_avaliacoes_google(ong['place_id'])
        positive_reviews = [review for review in reviews if analise_sentimento(review['text']) > 0]
        
        if positive_reviews:
            ongs_com_avaliacoes.append({
                'nome': ong['nome'],
                'site': ong['link'],
                'avaliacoes_positivas': len(positive_reviews)
            })
    
    # Ordena as ONGs com base no número de avaliações positivas
    ongs_com_avaliacoes = sorted(ongs_com_avaliacoes, key=lambda x: x['avaliacoes_positivas'], reverse=True)
    
    return ongs_com_avaliacoes[:5]  # Retorna as 5 melhores

# Função principal
def buscar_e_analisar_ongs():
    """Permite buscar e analisar ONGs de forma iterativa com consulta personalizada."""
    while True:
        print("\n🔎 Bem-vindo ao sistema de busca de ONGs!")
        print("Digite uma palavra-chave para pesquisar ONGs (ex: 'ONGs ambientais no Rio Grande do Sul'):")
        
        query = input("Sua pesquisa: ").strip()
        
        # Realiza a busca no Google
        ongs = buscar_ongs_no_google(query)
        
        if not ongs:
            print("\n⚠️ Nenhuma ONG encontrada. Tente uma nova pesquisa!")
            continuar = input("\nDeseja tentar novamente? (s/n): ").strip().lower()
            if continuar != 's':
                break
            continue

        # Classifica as ONGs com base nas avaliações positivas
        ongs_classificadas = classificar_ongs_por_avaliacoes(ongs)
        
        print("\n🏆 Top 5 ONGs com mais avaliações positivas:")
        for idx, ong in enumerate(ongs_classificadas, 1):
            print(f"{idx}. {ong['nome']}")
            print(f"   Site: {ong['site']}")
            print(f"   Avaliações Positivas: {ong['avaliacoes_positivas']}")
        
        print("\n🔗 Detalhes das ONGs encontradas:")
        for ong in ongs:
            print(f"Nome: {ong['nome']}")
            print(f"Descrição: {ong['snippet']}")
            print(f"Link: {ong['link']}")
        
        # Permite reiniciar o programa
        continuar = input("\nDeseja realizar outra pesquisa? (s/n): ").strip().lower()
        if continuar != 's':
            print("\nObrigado por usar o sistema de busca de ONGs! Até mais! 👋")
            break

# Executa o programa
if __name__ == "__main__":
    buscar_e_analisar_ongs()
