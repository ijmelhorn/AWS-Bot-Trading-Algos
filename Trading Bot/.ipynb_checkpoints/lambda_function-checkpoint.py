### Required Libraries ###
from datetime import datetime
### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }

def validate_data(age, investment_amount, intent_request):
    """
    Validates the data provided by the user.
    """

    # Validate that the user is over 18 years old
    if age is not None:
        age = parse_int(age)
        if age < 18:
           return build_validation_result(
                False,
                "age",
                "You should be at least 18 years old to use this service, please provide a different age.",
            )
       

    # Validate the investment amount, it should be > 1000
    if investment_amount is not None:
        investment_amount = parse_int(
            investment_amount
        )  
    # Since parameters are strings it's important to cast values
        if investment_amount <= 1000:
            return build_validation_result(
                False,
                "InvestmentAmount",
                "The amount to invest should be greater than 1000, please provide a correct amount in USD.",
            )

    # A True results is returned if age or amount are valid
    return build_validation_result(True, None, None)

### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


### Intents Handlers ###
def Cryptotrader(intent_request):
    """
    Performs dialog management and fulfillment for Trading bot.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["InvestmentAmount"]
    value = get_slots(intent_request)["value"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.

        ###  DATA VALIDATION CODE STARTS HERE ###
        validation_result = validate_data(age, investment_amount, intent_request)
        
        if not validation_result["isValid"]:
            return elicit_slot( intent_request["sessionAttributes"],
                                intent_request["currentIntent"]["name"],
                                get_slots(intent_request),
                                validation_result["violatedSlot"],
                                validation_result["message"]
                    )
                                
        ###  DATA VALIDATION CODE ENDS HERE ###

        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, get_slots(intent_request))

    # Get the initial Crypro value recommendation

    ###  Crypro value RECOMMENDATION CODE STARTS HERE ###

    if value == 'Ethereum':
        initial_recommendation = 'at $200 available on the model section of our website.'
    if value == 'Bitcoin':
        initial_recommendation ='at $200 available on the model section of  our website.'

    
    ###  Crypro value RECOMMENDATION CODE ENDS HERE ###


    # Return a message with the initial recommendation based on the value.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for answering.
            Based on the value you selected, my recommendation is to purchase our Golden Cross Support vector machine model {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )

 
### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "Cryptotrader":
        return Cryptotrader(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)