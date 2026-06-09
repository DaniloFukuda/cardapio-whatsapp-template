# 🍲 Cardápio WhatsApp Template

Um template genérico e responsivo de cardápio online para restaurantes. O cliente acessa pelo Instagram, monta o pedido e envia tudo pronto pelo WhatsApp!

## ✨ Características

- ✅ **Sem backend** - Funciona 100% no navegador
- ✅ **Sem React** - HTML, CSS e JavaScript puro
- ✅ **Mobile First** - Totalmente responsivo
- ✅ **LocalStorage** - Carrinho persistente
- ✅ **Inteligente** - Mensagem formatada para WhatsApp
- ✅ **Personalizável** - Fácil trocar nome, logo e produtos
- ✅ **Pronto para Production** - Design profissional

## 🚀 Como Usar

### 1. Abrir Localmente

1. Faça o download ou clone este repositório
2. Abra o arquivo `index.html` no navegador
3. Pronto! O site está funcionando

```bash
# Ou use um servidor local simples
python -m http.server 8000
# Depois acesse: http://localhost:8000
```

### 2. Personalizar o Restaurante

Edite o arquivo `config/restaurante.js`:

```javascript
const Restaurante = {
  nome: 'Seu Restaurante',
  slogan: 'Seu slogan aqui',
  whatsapp: '5511999999999', // Número com DDD, sem formatação
  instagram: '@seu.instagram',
  endereco: 'Rua...',
  horario: 'Seg-Dom: 11h às 22h',
  taxaEntregaPadrao: 5.00,
  aceitaEntrega: true,
  aceitaRetirada: true,
  cores: {
    principal: '#E74C3C',    // Vermelho principal
    secundaria: '#F39C12',   // Laranja
    fundo: '#FFF8F3',        // Bege claro
    texto: '#2C3E50'         // Texto escuro
  }
};
```

### 3. Adicionar/Editar Produtos

Edite o arquivo `data/cardapio.js`:

```javascript
const Cardapio = {
  categorias: [
    {
      id: 'marmitas',
      nome: 'Marmitas',
      descricao: 'Descrição da categoria',
      produtos: [
        {
          id: 'produto-1',
          nome: 'Nome do Produto',
          descricao: 'Descrição breve',
          preco: 25.00,
          imagem: '🍚' // Pode ser emoji ou URL
        }
        // ... mais produtos
      ]
    }
    // ... mais categorias
  ]
};
```

### 4. Publicar na Internet

#### Opção A: GitHub Pages (Grátis)

```bash
# 1. Crie um repositório no GitHub
# 2. Faça upload dos arquivos
# 3. Vá em Settings > Pages
# 4. Selecione "Deploy from a branch"
# 5. Escolha "main" branch
# 6. Seu site estará em: https://seu-usuario.github.io/cardapio-whatsapp-template
```

#### Opção B: Netlify (Grátis)

```bash
# 1. Acesse netlify.com
# 2. Clique em "New site from Git"
# 3. Conecte seu repositório GitHub
# 4. Deploy automático a cada push!
```

#### Opção C: Vercel (Grátis)

```bash
# Similar ao Netlify, acesse vercel.com
```

## 📁 Estrutura do Projeto

```
cardapio-whatsapp-template/
├── index.html              # Página inicial
├── cardapio.html           # Página do cardápio
├── pedido.html             # Página de checkout
│
├── config/
│   └── restaurante.js      # Configurações do restaurante 🔧
│
├── data/
│   └── cardapio.js         # Produtos e categorias 🔧
│
├── css/
│   └── style.css           # Estilos
│
├── js/
│   ├── app.js              # Lógica principal
│   ├── cart.js             # Gerenciador de carrinho
│   └── whatsapp.js         # Integração WhatsApp
│
├── assets/                 # Imagens, logos, etc
│
└── README.md               # Este arquivo
```

## 🔄 Fluxo do Usuário

1. **Página Inicial** (`index.html`) - Informações do restaurante
2. **Cardápio** (`cardapio.html`) - Escolhe produtos e adiciona ao carrinho
3. **Checkout** (`pedido.html`) - Preenche dados e confirma o pedido
4. **WhatsApp** - Abre o WhatsApp com a mensagem formatada pronta

## 💾 Como Funciona o Carrinho

- Os itens são salvos em `localStorage`
- Funcionam mesmo se fechar o navegador
- Limpa automaticamente após enviar o pedido

## 📱 Responsividade

O design é 100% mobile-first:
- ✅ Funciona em smartphones
- ✅ Funciona em tablets
- ✅ Funciona em desktops
- ✅ Botões grandes para mobile
- ✅ Navegação otimizada

## 🎨 Personalizando as Cores

As cores principais são definidas em `config/restaurante.js`:

```javascript
cores: {
  principal: '#E74C3C',    // Cor principal dos botões
  secundaria: '#F39C12',   // Cor secundária
  fundo: '#FFF8F3',        // Cor de fundo
  texto: '#2C3E50'         // Cor do texto
}
```

Você pode usar:
- Hex: `#E74C3C`
- RGB: `rgb(231, 76, 60)`
- Named colors: `red`

## 🔗 Links Úteis

- **Gerador de cores**: https://coolors.co/
- **Emojis**: https://emojipedia.org/
- **Paletas de cores para restaurante**: https://www.canva.com/learn/restaurant-color-schemes/

## ❓ Perguntas Frequentes

### Como colocar uma logo em vez de emoji?

Em `config/restaurante.js`:
```javascript
logo: 'https://seu-site.com/logo.png'
```

Depois em `index.html`, na linha onde tem `🍲`, mude para:
```html
<img src="URL_DA_LOGO" alt="Logo" style="width: 60px; height: 60px;">
```

### O número do WhatsApp não funciona

Certifique-se de:
1. Usar o número com código do país: `55` (Brasil)
2. Incluir o DDD: `11` (São Paulo)
3. Sem formatação: `5511987654321` ✅ (não `55 (11) 98765-4321` ❌)

### Posso adicionar múltiplas taxas de entrega por zona?

Sim! Edite `js/cart.js` e a lógica em `pedido.html` para calcular taxa baseada em endereço. Será necessário um pouco de JavaScript adicional.

### Como testar o WhatsApp localmente?

O link de WhatsApp funciona normalmente no navegador. Se tiver WhatsApp Web aberto, abrirá lá. Senão, redireciona para a versão web.

## 📄 Licença

Este projeto é de código aberto. Use livremente para seus projetos!

## 🤝 Contribuições

Encontrou um bug ou tem uma sugestão? Abra uma issue ou faça um pull request!

---

**Desenvolvido com ❤️ para pequenos e médios restaurantes**

Aproveite! 🎉
