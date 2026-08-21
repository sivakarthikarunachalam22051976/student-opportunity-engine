live_opportunities = []


def save_live_opportunities(opportunities):
    global live_opportunities

    live_opportunities = opportunities


def get_live_opportunity(opportunity_id: int):

    return next(
        (
            opportunity
            for opportunity in live_opportunities
            if opportunity.get("id") == opportunity_id
        ),
        None
    )


def get_all_live_opportunities():

    return live_opportunities