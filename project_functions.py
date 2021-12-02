def get_price(asset,from_date_var,to_date_var,interval_var):
    """
    function geared towards fetching crypto asset prices for a time period
    example call: get_price('bitcoin','2017-01-01','2021-12-01','1d')    
    """
    import san 
    

    df = san.get(
        "prices/"+asset,
        from_date=from_date_var,
        to_date=to_date_var,
        interval= interval_var    )


    return df