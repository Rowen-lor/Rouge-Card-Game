import pygame
import random
import sys
import os

# 初始化Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# 游戏状态
GAME_STATE = {
    'SELECT_CHARACTER': 0,
    'BATTLE': 1,
    'BUFF_SELECTION': 2,
    'GAME_OVER': 3
}

# 字体设置
def get_font(size):
    try:
        # 尝试使用微软雅黑
        return pygame.font.SysFont('microsoftyahei', size)
    except:
        # 如果找不到微软雅黑，使用系统默认字体
        return pygame.font.Font(None, size)

class Character:
    def __init__(self, name, health, attack, defense, description):
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.defense = defense
        self.description = description
        self.width = 200
        self.height = 300
        self.selected = False

    def draw(self, screen, x, y):
        color = GREEN if self.selected else WHITE
        pygame.draw.rect(screen, color, (x, y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (x, y, self.width, self.height), 2)
        
        font = get_font(24)
        name_text = font.render(self.name, True, BLACK)
        health_text = font.render(f"生命: {self.health}", True, BLACK)
        attack_text = font.render(f"攻击: {self.attack}", True, BLACK)
        defense_text = font.render(f"防御: {self.defense}", True, BLACK)
        desc_text = font.render(self.description, True, BLACK)
        
        screen.blit(name_text, (x + 10, y + 10))
        screen.blit(health_text, (x + 10, y + 40))
        screen.blit(attack_text, (x + 10, y + 70))
        screen.blit(defense_text, (x + 10, y + 100))
        screen.blit(desc_text, (x + 10, y + 130))

class Monster:
    def __init__(self, name, health, attack, defense):
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.defense = defense
        self.width = 150
        self.height = 200
        self.frozen = False
        self.frozen_duration = 0

    def draw(self, screen, x, y):
        pygame.draw.rect(screen, RED, (x, y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (x, y, self.width, self.height), 2)
        
        font = get_font(24)
        name_text = font.render(self.name, True, BLACK)
        health_text = font.render(f"生命: {self.health}/{self.max_health}", True, BLACK)
        attack_text = font.render(f"攻击: {self.attack}", True, BLACK)
        defense_text = font.render(f"防御: {self.defense}", True, BLACK)
        
        screen.blit(name_text, (x + 10, y + 10))
        screen.blit(health_text, (x + 10, y + 40))
        screen.blit(attack_text, (x + 10, y + 70))
        screen.blit(defense_text, (x + 10, y + 100))

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        return actual_damage

    def attack_player(self, player):
        if self.frozen:
            self.frozen_duration -= 1
            if self.frozen_duration <= 0:
                self.frozen = False
            return 0
        damage = max(1, self.attack - player.defense)
        player.health = max(0, player.health - damage)
        return damage

class Player:
    def __init__(self, character=None):
        self.character = character
        self.max_health = character.max_health if character else 100
        self.health = character.health if character else 100
        self.attack = character.attack if character else 10
        self.defense = character.defense if character else 5
        self.gold = 50
        self.luck = 1
        self.strength = 1
        self.agility = 1
        self.selected_card = None
        self.dragging_card = None
        self.drag_start_pos = None
        # 效果状态
        self.thunder_effect = False
        self.thunder_duration = 0

    def draw(self, screen):
        font = get_font(24)
        # 绘制玩家属性
        health_text = font.render(f"生命: {self.health}/{self.max_health}", True, BLACK)
        attack_text = font.render(f"攻击: {self.attack}", True, BLACK)
        defense_text = font.render(f"防御: {self.defense}", True, BLACK)
        gold_text = font.render(f"金币: {self.gold}", True, BLACK)
        luck_text = font.render(f"幸运: {self.luck}", True, BLACK)
        strength_text = font.render(f"力量: {self.strength}", True, BLACK)
        agility_text = font.render(f"敏捷: {self.agility}", True, BLACK)

        screen.blit(health_text, (10, 10))
        screen.blit(attack_text, (10, 30))
        screen.blit(defense_text, (10, 50))
        screen.blit(gold_text, (10, 70))
        screen.blit(luck_text, (10, 90))
        screen.blit(strength_text, (10, 110))
        screen.blit(agility_text, (10, 130))

    def draw_health_bar(self, screen, x, y, width, height):
        # 绘制血条背景
        pygame.draw.rect(screen, RED, (x, y, width, height))
        # 绘制当前血量
        current_width = int(width * (self.health / self.max_health))
        pygame.draw.rect(screen, GREEN, (x, y, current_width, height))

class Card:
    def __init__(self, name, attack, defense, cost, card_type="normal", effect=None):
        self.name = name
        self.attack = attack
        self.defense = defense
        self.cost = cost
        self.width = 100
        self.height = 150
        self.selected = False
        self.card_type = card_type  # normal, skill
        self.effect = effect  # 卡牌效果
        self.effect_duration = 0  # 效果持续回合数

    def draw(self, screen, x, y):
        # 根据卡牌类型选择颜色
        if self.card_type == "normal":
            color = GREEN if self.selected else WHITE
        elif self.card_type == "skill":
            color = BLUE if self.selected else (200, 200, 255)
        else:  # 默认颜色
            color = WHITE if self.selected else (200, 200, 200)

        pygame.draw.rect(screen, color, (x, y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (x, y, self.width, self.height), 2)
        
        # 绘制卡牌信息
        font = get_font(20)
        name_text = font.render(self.name, True, BLACK)
        attack_text = font.render(f"伤害: {self.attack}", True, BLACK)
        cost_text = font.render(f"费用: {self.cost}", True, BLACK)
        type_text = font.render(self.card_type, True, BLACK)
        
        screen.blit(name_text, (x + 5, y + 5))
        screen.blit(attack_text, (x + 5, y + 30))
        screen.blit(cost_text, (x + 5, y + 55))
        screen.blit(type_text, (x + 5, y + 80))

        # 如果有特殊效果，显示效果描述
        if self.effect:
            effect_text = font.render(self.effect, True, BLACK)
            screen.blit(effect_text, (x + 5, y + 105))

    def apply_effect(self, player, monster):
        if self.card_type == "normal":
            return self.attack
        elif self.card_type == "skill":
            if "雷" in self.name:
                player.thunder_effect = True
                player.thunder_duration = 2
                return self.attack
            elif "冰" in self.name:
                monster.frozen = True
                monster.frozen_duration = 1
                return self.attack
        return 0

class ScratchCard:
    def __init__(self, x, y, player):
        self.x = x
        self.y = y
        self.width = 150
        self.height = 100
        self.revealed = False
        self.player = player
        self.reward = self.generate_reward()
        self.scratched = False

    def generate_reward(self):
        # 根据玩家幸运值调整奖励概率
        rand = random.random() * self.player.luck
        if rand < 0.1:  # 10% 概率获得技能卡
            return self.generate_skill_card()
        elif rand < 0.3:  # 20% 概率获得重击
            return Card("重击", 10, 0, 2, "normal")
        else:  # 40% 概率获得普通攻击
            return Card("普通攻击", 5, 0, 1, "normal")

    def generate_skill_card(self):
        if random.random() < 0.5:  # 50% 概率获得雷属性
            return Card("雷击", 5, 0, 3, "skill", "后续2回合+3伤害")
        else:  # 50% 概率获得冰属性
            return Card("冰冻", 0, 0, 3, "skill", "怪物停止1回合")

    def draw(self, screen):
        if not self.scratched:
            pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        else:
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
            font = get_font(24)
            text = font.render(self.reward.name, True, BLACK)
            screen.blit(text, (self.x + 10, self.y + 40))

    def scratch(self, pos):
        if not self.scratched and self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height:
            self.scratched = True
            return self.reward
        return None

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("卡牌冒险")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 游戏状态
        self.game_state = GAME_STATE['SELECT_CHARACTER']
        self.player = None
        self.monster = None
        self.player_hand = []
        self.scratch_cards = []
        self.characters = [
            Character("战士", 120, 15, 8, "高生命值，中等攻击"),
            Character("法师", 80, 20, 5, "高攻击，低防御"),
            Character("游侠", 100, 12, 10, "平衡型角色")
        ]
        self.current_character = None
        self.battle_round = 0
        self.player_turn = True
        
        # 抽卡按钮
        self.draw_card_button = pygame.Rect(SCREEN_WIDTH - 150, 400, 120, 40)
        
        # 增益效果卡牌
        self.buff_cards = [
            Card("力量提升", 0, 0, 0, "buff", "攻击力+2"),
            Card("防御提升", 0, 0, 0, "buff", "防御力+2"),
            Card("生命恢复", 0, 0, 0, "buff", "恢复20点生命")
        ]

    def create_monster(self):
        return Monster("哥布林", 50, 8, 3)

    def create_initial_cards(self):
        # 创建初始卡牌
        self.player_hand = [
            Card("普通攻击", 5, 0, 1, "normal"),
            Card("普通攻击", 5, 0, 1, "normal"),
            Card("重击", 10, 0, 2, "normal"),
            Card("雷击", 5, 0, 3, "skill", "后续2回合+3伤害"),
            Card("冰冻", 0, 0, 3, "skill", "怪物停止1回合")
        ]
        
        # 创建刮刮卡
        if self.player:  # 确保玩家已经创建
            for i in range(3):
                self.scratch_cards.append(ScratchCard(50 + i * 200, 400, self.player))

    def draw_card(self):
        # 随机生成一张新卡牌
        rand = random.random() * self.player.luck
        if rand < 0.1:  # 10% 概率获得技能卡
            if random.random() < 0.5:  # 50% 概率获得雷属性
                return Card("雷击", 5, 0, 3, "skill", "后续2回合+3伤害")
            else:  # 50% 概率获得冰属性
                return Card("冰冻", 0, 0, 3, "skill", "怪物停止1回合")
        elif rand < 0.3:  # 20% 概率获得重击
            return Card("重击", 10, 0, 2, "normal")
        else:  # 40% 概率获得普通攻击
            return Card("普通攻击", 5, 0, 1, "normal")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == GAME_STATE['SELECT_CHARACTER']:
                    self.handle_character_selection(event.pos)
                elif self.game_state == GAME_STATE['BATTLE']:
                    # 检查是否点击抽卡按钮
                    if self.draw_card_button.collidepoint(event.pos):
                        new_card = self.draw_card()
                        self.player_hand.append(new_card)
                    else:
                        self.handle_battle_events(event.pos)
                elif self.game_state == GAME_STATE['BUFF_SELECTION']:
                    self.handle_buff_selection(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.game_state == GAME_STATE['BATTLE'] and self.player.dragging_card:
                    self.handle_card_drop(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                if self.game_state == GAME_STATE['BATTLE'] and self.player.dragging_card:
                    self.player.drag_start_pos = event.pos

    def handle_character_selection(self, pos):
        for i, character in enumerate(self.characters):
            x = 50 + i * 250
            y = 150
            if x <= pos[0] <= x + character.width and y <= pos[1] <= y + character.height:
                self.current_character = character
                self.player = Player(character)
                self.game_state = GAME_STATE['BATTLE']
                self.start_battle()

    def handle_battle_events(self, pos):
        if self.player_turn:
            # 处理卡牌选择
            for i, card in enumerate(self.player_hand):
                card_x = 50 + i * 120
                card_y = 400
                if card_x <= pos[0] <= card_x + card.width and card_y <= pos[1] <= card_y + card.height:
                    self.player.dragging_card = card
                    self.player.drag_start_pos = pos
                    break

    def handle_card_drop(self, pos):
        if self.player.dragging_card:
            # 检查是否拖到怪物区域
            monster_x = 500
            monster_y = 100
            if (monster_x <= pos[0] <= monster_x + self.monster.width and 
                monster_y <= pos[1] <= monster_y + self.monster.height):
                # 使用卡牌攻击怪物
                damage = self.player.dragging_card.apply_effect(self.player, self.monster)
                if damage > 0:
                    self.monster.take_damage(damage)
                # 如果玩家有雷属性效果，增加额外伤害
                if self.player.thunder_effect:
                    self.monster.take_damage(3)
                    self.player.thunder_duration -= 1
                    if self.player.thunder_duration <= 0:
                        self.player.thunder_effect = False
                self.player_hand.remove(self.player.dragging_card)
                self.player_turn = False
            self.player.dragging_card = None
            self.player.drag_start_pos = None

    def start_battle(self):
        self.monster = self.create_monster()
        self.battle_round = 1
        self.player_turn = True
        self.create_initial_cards()  # 在玩家创建后创建卡牌

    def handle_buff_selection(self, pos):
        # 处理增益卡牌选择
        for i, card in enumerate(self.buff_cards):
            card_x = 50 + i * 250
            card_y = 200
            if card_x <= pos[0] <= card_x + card.width and card_y <= pos[1] <= card_y + card.height:
                # 应用增益效果
                if "力量" in card.name:
                    self.player.attack += 2
                elif "防御" in card.name:
                    self.player.defense += 2
                elif "生命" in card.name:
                    self.player.health = min(self.player.max_health, self.player.health + 20)
                # 返回战斗状态
                self.game_state = GAME_STATE['BATTLE']
                self.start_battle()

    def update(self):
        if self.game_state == GAME_STATE['BATTLE']:
            if not self.player_turn and self.monster:
                # 怪物回合
                damage = self.monster.attack_player(self.player)
                self.player_turn = True
                
                # 检查战斗是否结束
                if self.player.health <= 0:
                    self.game_state = GAME_STATE['GAME_OVER']
                elif self.monster.health <= 0:
                    self.game_state = GAME_STATE['BUFF_SELECTION']

    def draw(self):
        self.screen.fill(WHITE)
        
        if self.game_state == GAME_STATE['SELECT_CHARACTER']:
            self.draw_character_selection()
        elif self.game_state == GAME_STATE['BATTLE']:
            self.draw_battle()
        elif self.game_state == GAME_STATE['BUFF_SELECTION']:
            self.draw_buff_selection()
        elif self.game_state == GAME_STATE['GAME_OVER']:
            self.draw_game_over()
        
        pygame.display.flip()

    def draw_character_selection(self):
        font = get_font(36)
        title = font.render("选择你的角色", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH//2 - 100, 50))
        
        for i, character in enumerate(self.characters):
            character.draw(self.screen, 50 + i * 250, 150)

    def draw_battle(self):
        # 绘制玩家属性
        self.player.draw(self.screen)
        self.player.draw_health_bar(self.screen, 10, 150, 200, 20)
        
        # 绘制怪物
        if self.monster:
            self.monster.draw(self.screen, 500, 100)
            # 绘制怪物血条
            pygame.draw.rect(self.screen, RED, (500, 80, 150, 10))
            current_width = int(150 * (self.monster.health / self.monster.max_health))
            pygame.draw.rect(self.screen, GREEN, (500, 80, current_width, 10))
            
            # 显示怪物状态
            font = get_font(20)
            if self.monster.frozen:
                frozen_text = font.render("冰冻中", True, BLUE)
                self.screen.blit(frozen_text, (500, 310))
        
        # 绘制手牌
        for i, card in enumerate(self.player_hand):
            if card != self.player.dragging_card:
                card.draw(self.screen, 50 + i * 120, 400)
        
        # 绘制正在拖动的卡牌
        if self.player.dragging_card and self.player.drag_start_pos:
            self.player.dragging_card.draw(self.screen, 
                                         self.player.drag_start_pos[0] - 50,
                                         self.player.drag_start_pos[1] - 75)

        # 显示回合信息
        font = get_font(24)
        turn_text = font.render("你的回合" if self.player_turn else "怪物回合", True, BLACK)
        self.screen.blit(turn_text, (SCREEN_WIDTH//2 - 50, 50))

        # 显示效果状态
        if self.player.thunder_effect:
            thunder_text = font.render(f"雷属性效果: {self.player.thunder_duration}回合", True, BLUE)
            self.screen.blit(thunder_text, (10, 350))

        # 绘制抽卡按钮
        pygame.draw.rect(self.screen, BLUE, self.draw_card_button)
        font = get_font(20)
        draw_text = font.render("抽卡", True, WHITE)
        text_rect = draw_text.get_rect(center=self.draw_card_button.center)
        self.screen.blit(draw_text, text_rect)

    def draw_buff_selection(self):
        font = get_font(36)
        title = font.render("选择增益效果", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH//2 - 100, 50))
        
        # 绘制增益卡牌
        for i, card in enumerate(self.buff_cards):
            # 绘制卡牌背景
            pygame.draw.rect(self.screen, WHITE, (50 + i * 250, 200, card.width, card.height))
            pygame.draw.rect(self.screen, BLACK, (50 + i * 250, 200, card.width, card.height), 2)
            
            # 绘制卡牌信息
            font = get_font(20)
            name_text = font.render(card.name, True, BLACK)
            effect_text = font.render(card.effect, True, BLACK)
            
            self.screen.blit(name_text, (55 + i * 250, 205))
            self.screen.blit(effect_text, (55 + i * 250, 230))
            
            # 绘制提示文字
            hint_text = font.render("点击选择", True, BLACK)
            self.screen.blit(hint_text, (55 + i * 250, 280))

    def draw_game_over(self):
        font = get_font(48)
        text = font.render("游戏结束", True, RED)
        self.screen.blit(text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit() 