def rsc(text: str):
    records = {}

    # Parse the text line by line, splitting on the first ":" to separate keys and values
    for line in text.splitlines():
        if ":" not in line:     continue
        
        k, v = line.split(":", 1)
        
        if not k:               continue                                                # lines like ":HL[...]"
            
        records[k] = v

    return records

