import env
import ast, re
from gmpy2 import is_prime
class Comb:
    numbers = []
    power = 0
    length = 0
    success = False
    def __str__(self):
        return f'Cards: {self.numbers}, Power: {self.power}, Length: {self.length}'

def get_cards(statement):
    'Get cards from the statement'
    expression = statement.replace(' ', '')
    try:
        tree = ast.parse(expression, mode='eval')
    except SyntaxError:
        return None
    try:
        val = ast.literal_eval(expression)
        if not val:
            return None
    except ValueError:
        return None

    for s in statement:
        if not s.isdigit() and s not in '=*() ': return None
    if len(re.findall('=', statement)) not in [0,2]: return None
    comb = Comb()
    comb.numbers = re.findall(r'\d+', statement)
    if isinstance(tree.body, ast.Compare):
        if not isinstance(tree.body.left, ast.Constant):
            return comb
        left = statement[:statement.index('=')] 
        comb.power = eval(left.replace(' ', ''))
        comb.length = len(re.findall(r'\d+', left))
        right = expression[expression.index('=')+2:]
    else:
        comb.power = eval(expression)
        comb.length = len(re.findall(r'\d+', statement))
        right = expression 
    val = ast.literal_eval(right)
    if val in [57, 1729]:
        comb.power = val
        comb.success = True
        return comb
    right_numbers = re.findall(r'\d+', right)
    for number in right_numbers:
        if not is_prime(int(number)):
            return comb
    comb.success = True
    return comb

if __name__ == '__main__':
    expression = "5"
    print(get_cards(expression))
