try:                from elements           import HeroButton, CounterLabel, Button, Label
except ImportError: from src.ui.elements    import HeroButton, CounterLabel, Button, Label

try:                from layout         import Layout, Resolution
except ImportError: from src.ui.layout  import Layout, Resolution