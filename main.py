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

# 资源路径
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
CHARACTERS_DIR = os.path.join(ASSETS_DIR, 'characters')
MONSTERS_DIR = os.path.join(ASSETS_DIR, 'monsters')
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, 'backgrounds')

# 加载图片函数
def load_image(path, size=None):
    try:
        image = pygame.image.load(path)
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except:
        print(f"无法加载图片: {path}")
        return None

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
        # 加载角色图片
        self.image = load_image(os.path.join(CHARACTERS_DIR, f"{name.lower()}.png"), (self.width, self.height))

    def draw(self, screen, x, y):
        color = GREEN if self.selected else WHITE
        pygame.draw.rect(screen, color, (x, y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (x, y, self.width, self.height), 2)
        
        # 绘制角色图片
        if self.image:
            screen.blit(self.image, (x, y))
        
        font = get_font(24)
        
        # 创建带描边的文字
        def draw_text_with_outline(text, pos, color=BLACK, outline_color=WHITE):
            # 绘制描边
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                outline = font.render(text, True, outline_color)
                screen.blit(outline, (pos[0] + dx, pos[1] + dy))
            # 绘制主文字
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, pos)
        
        # 绘制带描边的文字
        draw_text_with_outline(self.name, (x + 10, y + 10))
        draw_text_with_outline(f"生命: {self.health}", (x + 10, y + 40))
        draw_text_with_outline(f"攻击: {self.attack}", (x + 10, y + 70))
        draw_text_with_outline(f"防御: {self.defense}", (x + 10, y + 100))
        draw_text_with_outline(self.description, (x + 10, y + 130))

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
        # 加载怪物图片
        self.image = load_image(os.path.join(MONSTERS_DIR, f"{name.lower()}.png"), (self.width, self.height))

    def draw(self, screen, x, y):
        pygame.draw.rect(screen, RED, (x, y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (x, y, self.width, self.height), 2)
        
        # 绘制怪物图片
        if self.image:
            screen.blit(self.image, (x, y))
        
        font = get_font(24)
        
        # 创建带描边的文字
        def draw_text_with_outline(text, pos, color=BLACK, outline_color=WHITE):
            # 绘制描边
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                outline = font.render(text, True, outline_color)
                screen.blit(outline, (pos[0] + dx, pos[1] + dy))
            # 绘制主文字
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, pos)
            
        # 使用带描边的文字渲染方法
        draw_text_with_outline(self.name, (x + 10, y + 10))
        draw_text_with_outline(f"生命: {self.health}/{self.max_health}", (x + 10, y + 40))
        draw_text_with_outline(f"攻击: {self.attack}", (x + 10, y + 70))
        draw_text_with_outline(f"防御: {self.defense}", (x + 10, y + 100))

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
        self.max_health = character.max_health if character else 2000 # 默认最大生命值提高20倍
        self.health = character.health if character else 2000      # 默认当前生命值提高20倍
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
        
        # 加载背景图片
        self.backgrounds = {
            'menu': load_image(os.path.join(BACKGROUNDS_DIR, 'menu.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT)),
            'battle': load_image(os.path.join(BACKGROUNDS_DIR, 'battle.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT)),
            'buff': load_image(os.path.join(BACKGROUNDS_DIR, 'buff.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT)),
            'game_over': load_image(os.path.join(BACKGROUNDS_DIR, 'game_over.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT)) # 新增游戏结束背景
        }
        
        # 游戏状态
        self.game_state = GAME_STATE['SELECT_CHARACTER']
        self.player = None
        self.monster = None
        self.characters = [
            Character("战士", 2400, 15, 8, "高生命值，中等攻击"), # 120 * 20
            Character("法师", 1600, 20, 5, "高攻击，低防御"),   # 80 * 20
            Character("游侠", 2000, 12, 10, "平衡型角色")     # 100 * 20
        ]
        self.current_character = None
        self.battle_round = 0
        self.player_turn = True
        self.goblins_defeated = 0  # 哥布林击杀计数器
        
        # 定义事件按钮
        self.event_buttons = {
            'risk': pygame.Rect(50, 400, 120, 40),      # 风险型
            'balance': pygame.Rect(190, 400, 120, 40),  # 均衡型
            'safe': pygame.Rect(330, 400, 120, 40),     # 稳健型
            'all_in': pygame.Rect(470, 400, 120, 40),   # 梭哈
            'scratch': pygame.Rect(610, 400, 120, 40)   # 刮痧
        }
        
        # 增益效果卡牌
        self.buff_cards = [
            Card("力量提升", 0, 0, 0, "buff", "攻击力+2"),
            Card("防御提升", 0, 0, 0, "buff", "防御力+2"),
            Card("生命恢复", 0, 0, 0, "buff", "恢复20点生命")
        ]
        
        # 游戏结束界面的重新开始按钮
        self.restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 50, 150, 50)

    def create_monster(self):
        # 哥布林血量随击杀数增加，基础50，每击杀一只+50
        monster_health = 50 + (self.goblins_defeated * 50)
        return Monster("哥布林", monster_health, 8, 3)

    def start_battle(self):
        self.monster = self.create_monster()
        self.battle_round = 1
        self.player_turn = True

    def handle_character_selection(self, pos):
        for i, character in enumerate(self.characters):
            x = 50 + i * 250
            y = 150
            if x <= pos[0] <= x + character.width and y <= pos[1] <= y + character.height:
                self.current_character = character
                self.player = Player(character)
                self.goblins_defeated = 0 # 新游戏开始，重置击杀计数
                self.game_state = GAME_STATE['BATTLE']
                self.start_battle()

    def handle_battle_events(self, pos):
        if self.player_turn:
            # 检查是否点击了事件按钮
            for event_type, button in self.event_buttons.items():
                if button.collidepoint(pos):
                    self.trigger_event(event_type)
                    self.player_turn = False
                    break

    def trigger_event(self, event_type):
        if event_type == 'risk':
            # 风险型：75%概率扣30血，25%概率怪物扣50血
            if random.random() < 0.75:
                self.player.health = max(0, self.player.health - 30)
            else:
                self.monster.take_damage(50)
        elif event_type == 'balance':
            # 均衡型：50%概率扣20血，50%概率怪物扣20血
            if random.random() < 0.5:
                self.player.health = max(0, self.player.health - 20)
            else:
                self.monster.take_damage(20)
        elif event_type == 'safe':
            # 稳健型：25%概率扣10血，75%概率怪物扣10血
            if random.random() < 0.25:
                self.player.health = max(0, self.player.health - 10)
            else:
                self.monster.take_damage(10)
        elif event_type == 'all_in':
            # 梭哈：90%概率扣50血，10%概率怪物扣100血
            if random.random() < 0.9:
                self.player.health = max(0, self.player.health - 50)
            else:
                self.monster.take_damage(100)
        elif event_type == 'scratch':
            # 刮痧：100%概率怪物扣1血
            self.monster.take_damage(1)

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

    def restart_game(self):
        self.game_state = GAME_STATE['SELECT_CHARACTER']
        self.player = None
        self.monster = None
        self.current_character = None
        self.battle_round = 0
        self.player_turn = True
        # goblins_defeated 会在选择角色时重置

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == GAME_STATE['SELECT_CHARACTER']:
                    self.handle_character_selection(event.pos)
                elif self.game_state == GAME_STATE['BATTLE']:
                    self.handle_battle_events(event.pos)
                elif self.game_state == GAME_STATE['BUFF_SELECTION']:
                    self.handle_buff_selection(event.pos)
                elif self.game_state == GAME_STATE['GAME_OVER']:
                    if self.restart_button.collidepoint(event.pos):
                        self.restart_game()
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.game_state == GAME_STATE['BATTLE'] and hasattr(self.player, 'dragging_card') and self.player.dragging_card:
                    self.handle_card_drop(event.pos) # 虽然卡牌移除了，但以防万一保留调用
            elif event.type == pygame.MOUSEMOTION:
                if self.game_state == GAME_STATE['BATTLE'] and hasattr(self.player, 'dragging_card') and self.player.dragging_card:
                    self.player.drag_start_pos = event.pos

    def update(self):
        if self.game_state == GAME_STATE['BATTLE']:
            if not self.player_turn and self.monster:
                # 怪物回合
                if not self.monster.frozen: # 确保怪物没被冰冻
                    damage = self.monster.attack_player(self.player)
                else:
                    self.monster.frozen_duration -=1
                    if self.monster.frozen_duration <= 0:
                        self.monster.frozen = False
                self.player_turn = True
                
                # 检查战斗是否结束
                if self.player.health <= 0:
                    self.game_state = GAME_STATE['GAME_OVER']
                elif self.monster.health <= 0:
                    self.goblins_defeated += 1 # 击杀数增加
                    self.game_state = GAME_STATE['BUFF_SELECTION']

    def draw(self):
        # 绘制背景
        current_bg_key = 'menu' # 默认背景
        if self.game_state == GAME_STATE['SELECT_CHARACTER']:
            current_bg_key = 'menu'
        elif self.game_state == GAME_STATE['BATTLE']:
            current_bg_key = 'battle'
        elif self.game_state == GAME_STATE['BUFF_SELECTION']:
            current_bg_key = 'buff'
        elif self.game_state == GAME_STATE['GAME_OVER']:
            current_bg_key = 'game_over'
            
        if self.backgrounds.get(current_bg_key) and self.backgrounds[current_bg_key]:
            self.screen.blit(self.backgrounds[current_bg_key], (0,0))
        else:
            self.screen.fill(WHITE) # 图片不存在则填充白色
        
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
        # 添加标题背景
        title_bg = pygame.Surface((title.get_width() + 20, title.get_height() + 10))
        title_bg.fill(WHITE)
        title_bg.set_alpha(200)  # 设置半透明
        self.screen.blit(title_bg, (SCREEN_WIDTH//2 - title.get_width()//2 - 10, 40))
        
        # 绘制带描边的标题
        def draw_title_with_outline(text, pos, color=BLACK, outline_color=WHITE):
            # 绘制描边
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                outline = font.render(text, True, outline_color)
                self.screen.blit(outline, (pos[0] + dx, pos[1] + dy))
            # 绘制主文字
            text_surface = font.render(text, True, color)
            self.screen.blit(text_surface, pos)
        
        draw_title_with_outline("选择你的角色", (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        for i, character in enumerate(self.characters):
            # 添加角色信息背景
            info_bg = pygame.Surface((character.width, character.height))
            info_bg.fill(WHITE)
            info_bg.set_alpha(180)  # 设置半透明
            self.screen.blit(info_bg, (50 + i * 250, 150))
            
            # 绘制角色
            character.draw(self.screen, 50 + i * 250, 150)

    def draw_battle(self):
        # 绘制玩家属性
        # 添加属性信息背景
        attr_bg = pygame.Surface((200, 150))
        attr_bg.fill(WHITE)
        attr_bg.set_alpha(180)
        self.screen.blit(attr_bg, (10, 10))
        
        self.player.draw(self.screen)
        self.player.draw_health_bar(self.screen, 10, 150, 200, 20)
        
        # 绘制怪物
        if self.monster:
            # 添加怪物信息背景
            monster_bg = pygame.Surface((self.monster.width, self.monster.height))
            monster_bg.fill(WHITE)
            monster_bg.set_alpha(180)
            self.screen.blit(monster_bg, (500, 100))
            
            self.monster.draw(self.screen, 500, 100)
            # 绘制怪物血条
            pygame.draw.rect(self.screen, RED, (500, 80, 150, 10))
            current_width = int(150 * (self.monster.health / self.monster.max_health))
            pygame.draw.rect(self.screen, GREEN, (500, 80, current_width, 10))
        
        # 显示回合信息
        font_large = get_font(24)
        font_small = get_font(14) # 用于说明文字的较小字体
        turn_text = font_large.render("你的回合" if self.player_turn else "怪物回合", True, BLACK)
        turn_bg = pygame.Surface((turn_text.get_width() + 20, turn_text.get_height() + 10))
        turn_bg.fill(WHITE)
        turn_bg.set_alpha(180)
        self.screen.blit(turn_bg, (SCREEN_WIDTH//2 - turn_text.get_width()//2 - 10, 40))
        self.screen.blit(turn_text, (SCREEN_WIDTH//2 - turn_text.get_width()//2, 50))

        # 显示击败哥布林数量
        defeated_text = font_small.render(f"已击败哥布林: {self.goblins_defeated}", True, BLACK)
        defeated_bg = pygame.Surface((defeated_text.get_width() + 10, defeated_text.get_height() + 5))
        defeated_bg.fill(WHITE)
        defeated_bg.set_alpha(180)
        self.screen.blit(defeated_bg, (SCREEN_WIDTH - defeated_text.get_width() - 20, 10))
        self.screen.blit(defeated_text, (SCREEN_WIDTH - defeated_text.get_width() - 15, 12))

        # 绘制事件按钮及说明
        button_colors = {
            'risk': (255, 0, 0),      # 红色
            'balance': (255, 165, 0),  # 橙色
            'safe': (0, 255, 0),      # 绿色
            'all_in': (128, 0, 128),  # 紫色
            'scratch': (0, 0, 255)    # 蓝色
        }
        
        button_texts = {
            'risk': "风险型",
            'balance': "均衡型",
            'safe': "稳健型",
            'all_in': "梭哈",
            'scratch': "刮痧"
        }
        
        button_descriptions = {
            'risk': ["75%几率自身-30HP", "25%几率怪物-50HP"],
            'balance': ["50%几率自身-20HP", "50%几率怪物-20HP"],
            'safe': ["25%几率自身-10HP", "75%几率怪物-10HP"],
            'all_in': ["90%几率自身-50HP", "10%几率怪物-100HP"],
            'scratch': ["100%几率怪物-1HP"]
        }
        
        for event_type, button in self.event_buttons.items():
            # 绘制按钮背景
            pygame.draw.rect(self.screen, button_colors[event_type], button)
            pygame.draw.rect(self.screen, BLACK, button, 2)
            
            # 绘制按钮文字
            text = font_large.render(button_texts[event_type], True, WHITE)
            text_rect = text.get_rect(center=button.center)
            self.screen.blit(text, text_rect)
            
            # 绘制按钮说明 (支持换行)
            desc_lines = button_descriptions[event_type]
            line_y_offset = 0
            for line in desc_lines:
                desc_text_surface = font_small.render(line, True, BLACK)
                desc_text_rect = desc_text_surface.get_rect(center=(button.centerx, button.bottom + 20 + line_y_offset))
                
                # 添加说明文字背景
                desc_bg_width = desc_text_surface.get_width() + 10
                desc_bg_height = desc_text_surface.get_height() + 4
                desc_bg = pygame.Surface((desc_bg_width, desc_bg_height))
                desc_bg.fill(WHITE)
                desc_bg.set_alpha(200) # 设置半透明
                self.screen.blit(desc_bg, (desc_text_rect.left - 5, desc_text_rect.top - 2))
                self.screen.blit(desc_text_surface, desc_text_rect)
                line_y_offset += font_small.get_height() # 每行向下偏移字体高度

    def draw_buff_selection(self):
        font = get_font(36)
        title = font.render("选择增益效果", True, BLACK)
        # 添加标题背景
        title_bg = pygame.Surface((title.get_width() + 20, title.get_height() + 10))
        title_bg.fill(WHITE)
        title_bg.set_alpha(200)
        self.screen.blit(title_bg, (SCREEN_WIDTH//2 - title.get_width()//2 - 10, 40))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # 绘制增益卡牌
        for i, card in enumerate(self.buff_cards):
            # 添加卡牌背景
            card_bg = pygame.Surface((card.width, card.height))
            card_bg.fill(WHITE)
            card_bg.set_alpha(180)
            self.screen.blit(card_bg, (50 + i * 250, 200))
            
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
        font_large = get_font(48)
        font_medium = get_font(30)
        font_small = get_font(24)

        text = font_large.render("游戏结束", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(text, text_rect)

        # 显示最终击败哥布林数量
        score_text = font_medium.render(f"最终击败哥布林: {self.goblins_defeated}", True, BLACK)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
        self.screen.blit(score_text, score_rect)

        # 绘制重新开始按钮
        pygame.draw.rect(self.screen, GREEN, self.restart_button) # 绿色按钮
        pygame.draw.rect(self.screen, BLACK, self.restart_button, 2) # 黑色边框
        restart_text = font_small.render("重新开始", True, BLACK)
        restart_text_rect = restart_text.get_rect(center=self.restart_button.center)
        self.screen.blit(restart_text, restart_text_rect)

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