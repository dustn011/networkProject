# from random import *  # 랜덤 모듈 import
#
# words = ["apple", "banana", "orange"]  # 리스트에 영어 단어 후보를 나열
# word = choice(words)  # 랜덤으로 단어 중 1개를 선택
# # print("answer : " + word)  # 참고용으로 정답 출력 (실제 게임에서는 지우기)
# letters = ""  # 플레이어가 지금까지 입력한 알파벳들 저장
#
# # 정답을 맞힐 때까지 무한 반복
# while True:
#     succeed = True  # 성공 여부 확인 변수
#     print()
#     for w in word:  # 제시 단어를 알파벳별로 한 글자씩 비교
#         if w in letters:  # 현재 알파벳이 플레이어가 입력한 값들 중에 있으면
#             print(w, end=" ")  # 그 알파벳을 표시
#         else:  # 입력한 값들 중에 없으면
#             print("_", end=" ")  # 밑줄을 표시
#             succeed = False  # 밑줄이 있다는 것은 아직 다 풀지 못했음을 의미 !
#     print()
#
#     if succeed:  # 만약 성공했다면 게임 종료
#         print("성공")
#         break
#
#     letter = input("한글자 입력하세요 > ")  # 플레이어로부터 한 글자씩 입력
#     if letter not in letters:  # 입력값 중에 포함되어 있지 않다면
#         letters += letter  # 새로 입력받은 글자를 입력값에 추가
#
#     if letter in word:  # 입력한 글자가 제시 단어에 포함되었다면
#         print("정답")
#     else:  # 포함되어있지 않다면
#         print("땡")

# import random
# def hangman(word):
#     wrong = 0
#     stages = ["",
#              "________        ",
#              "|               ",
#              "|        |      ",
#              "|        0      ",
#              "|       /|\     ",
#              "|       / \     ",
#              "|               "
#              ]
#     rletters = list(word)
#     board = ["_"] * len(word)
#     win = False
#     print("Welcome to Hangman")
#     while wrong < len(stages) - 1:
#         print("\n")
#         msg = "글자를 입력하세요: "
#         char = input(msg)
#         if char in rletters:
#             cind = rletters.index(char)
#             board[cind] = char
#             rletters[cind] = '$'
#         else:
#             wrong += 1
#         print((" ".join(board)))
#         e = wrong + 1
#         print("\n".join(stages[0: e]))
#         if "_" not in board:
#             print("You win!")
#             print(" ".join(board))
#             win = True
#             break
#     if not win:
#         print("\n".join(stages[0: wrong]))
#         print("행맨이 죽었습니다 정답은 : {}.".format(word))
#
# words = ["python", "java", "kotlin", "javascript", "ruby"]
# word = random.choice(words)
# hangman(word)

import pygame
import sys
from pygame.locals import *

pygame.init()
clock = pygame.time.Clock()

WIDTH, HEIGHT = 800 ,500
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Hangman")

WHITE = (255,255,255)
BLACK = (0,0,0)

while True:
    for event in pygame.event.get():
        if e