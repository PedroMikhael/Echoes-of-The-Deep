# Echoes of the Deep

Jogo 2D de exploração submarina desenvolvido em Python/Pygame para a disciplina de Computação Gráfica 

## Descrição

O jogador controla um submarino de pesquisa nas profundezas do oceano, onde existem alguns animais e bombas aquáticas que podem atacar o jogador. O objetivo é encontrar cápsulas de pesquisa perdidas navegando por cavernas escuras utilizando a lanterna do submarino e o sonar antes que a bateria do submarino acabe totalmente.

## Demonstração

**Vídeo de execução**: https://youtu.be/WO6NzV6TZ_4

## Estrutura do Projeto

```
jogo_pygame/
├── src/
│   ├── main.py
│   ├── primitives.py
│   ├── transforms.py
│   ├── menu.py
│   ├── map.py
│   ├── minimap.py
│   ├── flashlight.py
│   └── characters/
│       ├── submarine.py
│       ├── jellyfish.py
│       ├── tentacles.py
│       ├── water_bomb.py
│       └── research_capsule.py
├── imagens/
├── sounds/
├── requirements.txt
├── demonstração.mp4
└── README.md
```

## Requisitos

- Python 3.8+
- Pygame

## Instalação e Execução

```bash
# Clonar repositório
git clone https://github.com/PedroMikhael/jogo_pygame.git
cd jogo_pygame

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual (Windows)
.\venv\Scripts\activate

# Instalar dependências
pip install -r requiriments.txt

# Executar o jogo
python src/main.py
```

## Controles

| Tecla | Ação |
|-------|------|
| Setas direcionais | Mover submarino |
| Espaço | Ativar sonar |
| ESC | Pausar |


## Equipe

- Pedro Mikhael
- João Victor
- Rian Vilanova
- Bianca Leão
- Fabio Stahl

## Licença

Projeto acadêmico desenvolvido para a disciplina de Computação Gráfica.
