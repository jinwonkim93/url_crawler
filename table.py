# import things
from flask_table import Table, Col

# Declare your table
class ItemTable(Table):
    title = Col('Title')
    description = Col('Description')
    url = Col('Url')
    image = Col('image')

# Get some objects
class Item(object):
    def __init__(self, title, description, url, image):
        self.title = title
        self.description = description
        self.url = url
        self.image = image

items = [Item('Name1', 'Description1'),
         Item('Name2', 'Description2'),
         Item('Name3', 'Description3')]
# Or, equivalently, some dicts
items = [dict(name='Name1', description='Description1', url = 'sdfsdf', image = 'fififi'),
         dict(name='Name2', description='Description2'),
         dict(name='Name3', description='Description3')]

# Or, more likely, load items from your database with something like
#items = ItemModel.query.all()

# Populate the table
table = ItemTable(items)

# Print the html
print(table.__html__())
# or just {{ table }} from within a Jinja template