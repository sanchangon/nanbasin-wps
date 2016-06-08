import zoo
def Hello(conf,inputs,outputs):
    outputs["Result"]["value"]=\
            "Hello "+inputs["name"]["value"]+" from the Naresuan University @ ZOO-Project Python world !"
    return zoo.SERVICE_SUCCEEDED

