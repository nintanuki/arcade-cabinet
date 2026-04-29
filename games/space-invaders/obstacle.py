import pygame 

class Block(pygame.sprite.Sprite):
	def __init__(self,size,color,x,y):
		super().__init__()
		self.image = pygame.Surface((size,size))
		self.image.fill(color)
		self.rect = self.image.get_rect(topleft = (x,y))

# default
shape = [
'  xxxxxxx',
' xxxxxxxxx',
'xxxxxxxxxxx',
'xxxxxxxxxxx',
'xxxxxxxxxxx',
'xxx     xxx',
'xx       xx']

# heart
# shape = [
# '  xxx   xxx  ',
# ' xxxxx xxxxx ',
# 'xxxxxxxxxxxxx',
# 'xxxxxxxxxxxxx',
# ' xxxxxxxxxxx ',
# '  xxxxxxxxx  ',
# '   xxxxxxx   ',
# '    xxxxx    ',
# '     xxx     ',
# '      x      '
# ]

# diamond
# shape = [
# '      x      ',
# '     xxx     ',
# '    xxxxx    ',
# '   xxxxxxx   ',
# '  xxxxxxxxx  ',
# ' xxxxxxxxxxx ',
# '  xxxxxxxxx  ',
# '   xxxxxxx   ',
# '    xxxxx    ',
# '     xxx     ',
# '      x      '
# ]

# arrow
# shape = [
# '      x      ',
# '     xxx     ',
# '    xxxxx    ',
# '   xxxxxxx   ',
# '  xxxxxxxxx  ',
# ' xxxxxxxxxxx ',
# '     xxx     ',
# '     xxx     ',
# '     xxx     '
# ]

# smily face
# shape = [
# '  xxxxxxxxx  ',
# ' xx       xx ',
# 'xx  x   x  xx',
# 'xx         xx',
# 'xx  xxxxx  xx',
# ' xx       xx ',
# '  xxxxxxxxx  ',
# ]

# rocket
# shape = [
# '      x      ',
# '     xxx     ',
# '    xxxxx    ',
# '   xxxxxxx   ',
# '   xxxxxxx   ',
# '   xx   xx   ',
# '   xx   xx   ',
# '  xxxxxxxxx  ',
# ' xxxxxxxxxxx ',
# '    xx xx    '
# ]