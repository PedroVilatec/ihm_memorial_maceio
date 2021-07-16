# GUI

## Overview

O projeto consiste em uma interface gráfica responsável pelo controle e emissão de sinais para leds RGB

O software se divide em algumas etapas:

1. SERVIDOR

	O servidor, a princípio será um raspberry pi instalado numa caixa metálica com os demais circuitos.  O servidor receberá comandos
de um terminal toutchscreen (raspberry pi) e de um controle remoto rf. O servidor irá controlar a iluminação led rgb via wifi, comandar
um esp8266 para controlar um ar condicionado, a entrada e saída de uma mesa motorizada, a abertura e fechamento de uma porta, o 
acionamento de uma maquina de fumaça e o acionamento de uma esteira através da placa do projeto arduino.



2. TERMINAL

  O terminal será uma raspberry com uma tela toutchscreen com interface gráfica, em que os usuários poderão alterar as cores dos leds rgb, solicitar a reprodução de um áudio ao servidor, e controlar o ar condicionado. 

  

Na aba de iluminação o sistema terá nove scenários para o usuário ir passando a imagem e conforme ele muda de tela a iluminação deverá alterar
para os valores previamente configurados. Ao abrir cada imagem o sistema deverá setar os controladores de led com os valores RGB 

ex.: SCENARIO 01 = Sanca 01 controlador "8KNNCLL" RGB(255,146,156)
				   Sanca 02 controlador "BGBHNSA" RGB(12,200,240)
				   Sanca 03 controlador "8KNNCLL" RGB(128,0,255)
				   
cada transição de cena deverá ocorrer suavemente até o status rgb atual, ficar igual ao novo status.


3. CONTROLADOR LED WIFI

Os contoladores de led wifi (que utilizam esp8285) tem ima id própria. Deverá ser atribuido uma relação entre o id e o nome da sanca para facilitar sua identificação.



## Dependências

### Pyautogiu

Para instalar a biblioteca, é preciso baixar através do comando 

#### Windows

`C:\>pip install pyautogui`

#### Linux

```
sudo apt-get install scrot
sudo apt-get install python3-tk
sudo apt-get install python3-dev
pip3 install pyautogui
```






### PyQt5

```
pip3 install pyqt5
```







## TODO

- [x] Commit inicial
- [ ] Definição da plataforma
- [ ] Descrição e divisão das tarefas

## Ajuda


* [Uso do git](http://rogerdudler.github.io/git-guide/index.pt_BR.html)
* [Entendendo o gitflow](https://medium.com/trainingcenter/utilizando-o-fluxo-git-flow-e63d5e0d5e04)
=======
Para compilar o arquivo `.ui` gerado a partir do [QtDesigner](https://www.codementor.io/deepaksingh04/design-simple-dialog-using-pyqt5-designer-tool-ajskrd09n) é preciso abrir o `Prompt de Comando`  e digitar os seguintes comandos, para gerar o arquivo `.py`que contém a classe da interface criada. 

```shell
pyuic5 VilatecClientApp.ui > VilatecClientApp.py
pyrcc5 -o images_rc.py images.qrc
```



**A segunda linha de comando** é parar que seja gerado o arquivo de recurso para ser importado no arquivo principal. No cenário atual, faz-se necessário que o código com a lógica seja **colado** no corpo do arquivo VilatecClientApp.py. 



## Links úteis

[Uso do git](http://rogerdudler.github.io/git-guide/index.pt_BR.html)
[Entendendo o gitflow](https://medium.com/trainingcenter/utilizando-o-fluxo-git-flow-e63d5e0d5e04)
>>>>>>> celso



Aqui estão descritos algumas opções de gerenciadores de git, para *facilitar* a utilização da ferramenta

* [TortoiseGit](https://tortoisegit.org/)
* [GitKraken](https://www.gitkraken.com/)
* [Git-Cola](https://git-cola.github.io/)

