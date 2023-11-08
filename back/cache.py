from aiocache import Cache
pricing = Cache(Cache.MEMORY) # prices to return to client

# pricing = dict()

"""
pricing = {
    "key": {
        "is_done": boolean,
        "img1": ""          # Location of result image 1
        "img2": ""          # Location of result image 2
        "mk": [],           # Market prices
        "bs": [],           # Black Scholes
        "mc": [],           # Monte Carlo
        "bs_ivo": [],       # Black Scholes from IVolatility.com
        "garch": [],        # GARCH(1,1)
        "gp": [],           # Gaussian Process
        "gp_status"
    }
}
"""