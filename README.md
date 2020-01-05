# League-Time-Tracker
 This is to track my friend Stellar Pan's progress in the Summoners Rift.
 This script calls the Riot API to generate a graph of number of hours played per day.
 
 I have hosted this script on AWS Lambda.
 The following link will act as an API gateway to see the result of the script
 https://qerzfw3nxa.execute-api.us-east-1.amazonaws.com/default/League_Time_Tracker
 
 There are 2 parameters user_name and days.
 For example, to look up how many hous Xeyukie played in the past 6 days, go to this link:
 https://qerzfw3nxa.execute-api.us-east-1.amazonaws.com/default/League_Time_Tracker?user_name=Xeyukie&days=6
 
 
 
