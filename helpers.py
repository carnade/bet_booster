def create_statistics_response(games_list, standings):
    threshholdBetGood = 7
    threshholdBetDecent = 4
    threshholdOUGood = 10
    threshholdOUDecent = 7


    result = {}
    stats = {
        "totalGames": 0,
        "over": 0,
        "under": 0,
        "OUTie" : 0,
        "coveredLoss": 0
    }
    predictions = {
        "predictedOverGood": 0,
        "predictedOverGoodWin": 0,
        "predictedUnderGood": 0,
        "predictedUnderGoodWin": 0,
        "predictedOverDecent": 0,
        "predictedOverDecentWin": 0,
        "predictedUnderDecent": 0,
        "predictedUnderDecentWin": 0,
        "betGood": 0,
        "betGoodWin": 0,
        "betDecent": 0,
        "betDecentWin": 0,
        "valueUpset": 0,
        "valueUpsetWin": 0
    }

    for game in games_list:
        try:
            if "results" in game:
                calced_ou = calc_predicted_overunder(standings, game['HomeTeam'], game['AwayTeam'])
                game_result = game["results"]
                stats["totalGames"] += 1
                homeScore = int(game_result["HomeScore"])
                awayScore = int(game_result["AwayScore"])
                totalScore = homeScore + awayScore
                ou_diff = calced_ou - totalScore
                homeFav = float(game["HomeHandicap"]) < float(game["AwayHandicap"])

                if calced_ou - threshholdOUGood > float(game["OverUnder"]):
                    predictions["predictedOverGood"] += 1
                elif calced_ou + threshholdOUGood < float(game["OverUnder"]):
                    predictions["predictedUnderGood"] += 1
                elif calced_ou - threshholdOUDecent > float(game["OverUnder"]):
                    predictions["predictedOverDecent"] += 1
                elif calced_ou + threshholdOUDecent < float(game["OverUnder"]):
                    predictions["predictedUnderDecent"] += 1
                if float(game["OverUnder"]) < totalScore:
                    stats["over"] += 1
                    if calced_ou >= float(game["OverUnder"]):
                        if ou_diff >= threshholdOUGood:
                            predictions["predictedOverGoodWin"] += 1
                        elif ou_diff >= threshholdOUDecent:
                            predictions["predictedOverDecentWin"] += 1

                elif float(game["OverUnder"]) > totalScore:
                    stats["under"] += 1
                    if calced_ou <=  float(game["OverUnder"]):
                        if abs(ou_diff) >= threshholdOUGood:
                            predictions["predictedOverGoodWin"] += 1
                        elif abs(ou_diff) >= threshholdOUDecent:
                            predictions["predictedOverDecentWin"] += 1
                else:
                    stats["OUTie"] += 1
                if abs(homeScore - awayScore) <= abs(float(game["HomeHandicap"])):
                    if homeScore > awayScore and homeFav:
                      stats["coveredLoss"] += 1
                    if homeScore < awayScore and not homeFav:
                      stats["coveredLoss"] += 1



                # Splitting the 'L10' value of home team and converting the wins part to float, then multiplying by l10_mult
                home_team_standing = standings[game['HomeTeam']]#next((standing for standing in standings if standing['Team'] == game['HomeTeam']), None)

                away_team_standing = standings[game['AwayTeam']]#next((standing for standing in standings if standing['Team'] == game['AwayTeam']), None)


                game_value = calc_game_value(game, home_team_standing, away_team_standing)
                if game_value >= threshholdBetGood or game_value <= -threshholdBetGood:
                    predictions["betGood"] += 1
                    if game_value >= threshholdBetGood and homeScore > awayScore:
                        predictions["betGoodWin"] += 1
                    if game_value <= -threshholdBetGood and homeScore < awayScore:
                        predictions["betGoodWin"] += 1
                elif game_value >= threshholdBetDecent or game_value <= -threshholdBetDecent:
                    predictions["betDecent"] += 1
                    if game_value >= threshholdBetDecent and homeScore > awayScore:
                        predictions["betDecentWin"] += 1
                    if game_value <= -threshholdBetDecent and homeScore < awayScore:
                        predictions["betDecentWin"] += 1
                if (homeFav and game_value < 0) or (not homeFav and game_value > 0):
                    predictions["valueUpset"] = +1
                    if (homeFav and homeScore < awayScore) or (not homeFav and homeScore > awayScore):
                        predictions["valueUpsetWin"] = +1


                '''
        "predictedOverGood": 0,
        "predictedOverGoodWin": 0,
        "predictedUnderGood": 0,
        "predictedUnderGoodWin": 0,
        "predictedOverDecent": 0,
        "predictedOverDecentWin": 0,
        "predictedUnderDecent": 0,
        "predictedUnderDecentWin": 0,
        "betGood": 0,
        "betGoodWin": 0,
        "betDecent": 0,
        "betDecentWin": 0,
        "valueUpset": 0,
        "valueUpsetWin": 0'''

        except Exception as e:
            print(e)
    result["stats"] = stats
    result["predictions"] = predictions
    return result

def calc_predicted_overunder(standings, home_team, away_team):
    home_score = float(standings[home_team]["PPG"]) + float(standings[home_team]["OPPG"])
    away_score = float(standings[away_team]["PPG"]) + float(standings[away_team]["OPPG"])
    game_score = float(standings[home_team]["PPG"]) + float(standings[away_team]["PPG"])
    return round((home_score + away_score + game_score)/3, 1)

def calc_game_value(game, home_team_standing, away_team_standing):
    home_advantage = 2
    game_mult = 20
    l10_mult = 0.3
    l10_h_value = float(home_team_standing['L10'].split('-')[0]) * l10_mult

    # Calculating the home value based on the formula provided
    home_value = ((float(home_team_standing['Wins']) / home_team_standing[
        'Games']) * game_mult) + home_advantage + l10_h_value
    l10_a_value = float(away_team_standing['L10'].split('-')[0]) * l10_mult
    away_value = ((float(away_team_standing['Wins']) / away_team_standing['Games']) * game_mult) + l10_a_value
    game_value = round(home_value - away_value, 1)
    return game_value


