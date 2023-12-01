from back.garch.main import GARCH
from datetime import datetime
from back.utils import dte_count
# 
start = datetime.strptime("1990-01-02", "%Y-%m-%d")
end = datetime.strptime("2009-08-10", "%Y-%m-%d")

model = GARCH()
model.InitializeData(start, end, "^SPX")
model.Optimize()
print(model.params)

