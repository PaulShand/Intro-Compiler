import re

def LVN(program):
    #initialize list to keep track of data
    # keeps a list of newly made virtual registers
    new_vars = []
    # keeps a list of the created basic blocks
    basic_blocks = []
    # keeps a list of instructions per block
    bb = []
    # counter of edited lines of code
    edited_line = 0
    # create blocks from program
    for inst in program:
        # if either branch or label is found then it will create a new block
        if inst.find("branch") != -1 or inst.find("label") != -1:
            # append current lsit of inst then make the branch a separate block then a reset the instruction list
            if bb:
                basic_blocks.append(bb)
            bb = [inst]  
            basic_blocks.append(bb)  
            bb = []  
        else:
            bb.append(inst)  
    # If there's any leftover block add the last block to basic_blocks if it is not empty
    if bb: 
        basic_blocks.append(bb) 


    # create a new block list to store the changed inst
    new_basic_blocks = []
 
    # iterate through block to enumerate virtual registers
    for block in basic_blocks:
        # keep track of the latest number called and increment counter to number variable
        counter = 0 
        latest_numbers = {}
        new_block = []
        for inst in block:
            # scan for the three types of command
            match_two_operand = re.match(r"(\S+) = (\S+)\((\S+),(\S+)\)", inst.strip())
            match_single_operand = re.match(r"(\S+) = (\S+)\((\S+)\)", inst.strip())
            match_assignment = re.match(r"(\S+) = ([\w\d_]+);", inst.strip())

            # if the instruction is a two-operand operation
            if match_two_operand:  

                destination, operation, operand1, operand2 = match_two_operand.groups()

                # numbering the operand1
                # endure it's a vr or new_name
                if operand1.startswith("vr") or operand1.startswith("_new_name"):
                    # if operand never seen before add to latest number and increment counter
                    if operand1 not in latest_numbers:
                        latest_numbers[operand1] = counter
                        counter += 1
                    # depending on if it was found in latest it will either get new number or previous one
                    new_var1 = f"{operand1}_{latest_numbers[operand1]}"
                    # keep track of new variables being created
                    if new_var1 not in new_vars:
                        new_vars.append(new_var1)
                else:
                    new_var1 = operand1

                # numbering the operand2
                if operand2.startswith("vr") or operand2.startswith("_new_name"):
                    if operand2 not in latest_numbers:
                        latest_numbers[operand2] = counter
                        counter += 1
                    new_var2 = f"{operand2}_{latest_numbers[operand2]}"
                    if new_var2 not in new_vars:
                        new_vars.append(new_var2)
                else:
                    new_var2 = operand2
                    

                # updating the instruction
                if destination.startswith("vr") or destination.startswith("_new_name"):
                    new_dest = f"{destination}_{counter}"
                    if new_dest not in new_vars:
                        new_vars.append(new_dest)
                    latest_numbers[destination] = counter
                    counter += 1
                else:
                    new_dest = destination

                # add new instruction
                new_instruction = f"{new_dest} = {operation}({new_var1},{new_var2});"
                new_block.append(new_instruction)

            # if the instruction is a single-operand operation
            elif match_single_operand:  
                destination, operation, operand = match_single_operand.groups()

                # numbering the operand
                if operand.startswith("vr") or operand.startswith("_new_name"):
                    if operand not in latest_numbers:
                        latest_numbers[operand] = counter
                        counter += 1
                    new_var = f"{operand}_{latest_numbers[operand]}"
                    if new_var not in new_vars:
                        new_vars.append(new_var)
                else:
                    new_var = operand

                # updating the instruction
                if destination.startswith("vr") or destination.startswith("_new_name"):
                    new_dest = f"{destination}_{counter}"
                    if new_dest not in new_vars:
                        new_vars.append(new_dest)
                    latest_numbers[destination] = counter
                    counter += 1
                else:
                    new_dest = destination
                new_instruction = f"{new_dest} = {operation}({new_var});"
                new_block.append(new_instruction)

              # if the instruction is an assignment
            elif match_assignment:
                left_var, right_var = match_assignment.groups()

                # Numbering the right_var
                if right_var.startswith("vr") or right_var.startswith("_new_name"):
                    if right_var not in latest_numbers:
                        latest_numbers[right_var] = counter
                        counter += 1
                    new_var = f"{right_var}_{latest_numbers[right_var]}"
                    if new_var not in new_vars:
                        new_vars.append(new_var)
                else:
                    new_var = right_var

                # numbering the left_var (if needed)
                if left_var.startswith("vr") or left_var.startswith("_new_name"):
                    new_left_var = f"{left_var}_{counter}"
                    if new_left_var not in new_vars:
                        new_vars.append(new_left_var)
                    latest_numbers[left_var] = counter
                    counter += 1
                else:
                    new_left_var = left_var
                # updating the instruction
                new_instruction = f"{new_left_var} = {new_var};"
                new_block.append(new_instruction)

            else:  # if the instruction is a return
                new_block.append(inst)

            
        new_basic_blocks.append(new_block)
    
    # new variables to commit lvn
    new_opt_basic = []
    for block in new_basic_blocks:
        # dictionary to keep track of operation like lecture says
        H = {}
        Known = {}
        latest = {}
        new_opt_block = []
        for inst in block:
            #same scanner as above
            match_two_operand = re.match(r"(\S+) = (\S+)\((\S+),(\S+)\)", inst.strip())
            match_single_operand = re.match(r"(\S+) = (\S+)\((\S+)\)", inst.strip())
            match_assignment = re.match(r"(\S+) = ([\w\d_]+);", inst.strip())

            if match_two_operand:
                destination, operation, operand1, operand2 = match_two_operand.groups()

                # always order operation by aplhabetical order
                if operand1 > operand2:
                    op = f"{operand1} + {operand2}"
                else:
                    op = f"{operand2} + {operand1}"

                # works for the following inst
                if operation in ["addi", "multi", "addf", "multf"]:
                    
                    # check if op is in H
                    for key, value in H.items():
                        if op == value:
                            # print(op)
                            # print(value)
                            # print(inst)
                            
                            # grab each operand name and number
                            if operand1.startswith("vr"):
                                oper1_name = operand1.split('_')[0]
                                oper1_num = operand1.split('_')[1]
                            elif operand1.startswith("_new_name"):
                                oper1_name = operand1.rpartition('_')[0]
                                oper1_num = operand1.rpartition('_')[2]
                                

                            if operand2.startswith("vr"):
                                oper2_name = operand2.split('_')[0]
                                oper2_num = operand2.split('_')[1]
                            elif operand2.startswith("_new_name"):
                                oper2_name = operand2.rpartition('_')[0]
                                oper2_num = operand2.rpartition('_')[2]
                                
                            # if operand name is in latest version then check it's the correct number
                            if oper1_name in latest and oper2_name in latest:
                                if latest[oper1_name] == oper1_num and latest[oper2_name] == oper2_num:
                                    inst = f"{destination} = {key};"

                                    edited_line += 1
                                    break
                            # if neither in it then update and increment edited lines
                            elif oper1_name not in latest and oper2_name not in latest:
                                inst = f"{destination} = {key};"
                                #print(inst)
                                edited_line += 1
                                break
                            
                    # store the operator
                    H[destination] = op

                            


            elif match_single_operand:
                destination, operation, operand = match_single_operand.groups()
                # check to be an intiger and id so store
                if operand.isdigit():
                    Known[destination] = operand
                ## if vr or new name update latest
                if destination.startswith("vr"):
                    latest[destination.split('_')[0]] = destination.split('_')[1]
                if destination.startswith("_new_name"):
                    latest[destination.rpartition('_')[0]] = destination.rpartition('_')[2]
                
                # print("1:",inst)


            elif match_assignment:
                destination, operand = match_assignment.groups()
                #if var is known transfer the known value
                if operand in Known:
                    Known[destination] = Known[operand]
                # if start with vr or new_name add to latest
                if destination.startswith("vr"):
                    latest[destination.split('_')[0]] = destination.split('_')[1]
                if destination.startswith("_new_name"):
                    latest[destination.rpartition('_')[0]] = destination.rpartition('_')[2]

                #add to possibilities in H dictionary
                if operand in H:
                    H[destination] = H[operand]

                # print("0:",inst)



            new_opt_block.append(inst)
        # print("new block")
        # print(Known)
        # print(latest)
        # print(H)
        new_opt_basic.append(new_opt_block)
    # print(new_opt_basic)
    
        
    #finally stitch back together
    new_new_basic = []
    for new_block in new_opt_basic:

        # first add a prepend to stitich back all var that is first called then scan block to save all destination
        assigned_vars = []  
        to_prepend = []  
        for inst in new_block:

            match_two_operand = re.match(r"(\S+) = (\S+)\((\S+),(\S+)\)", inst.strip())
            match_single_operand = re.match(r"(\S+) = (\S+)\((\S+)\)", inst.strip())
            match_assignment = re.match(r"(\S+) = ([\w\d_]+);", inst.strip())


            if match_two_operand:
                destination, operation, operand1, operand2 = match_two_operand.groups()
                # remember all assigned var
                assigned_vars.append(destination)
                # then if the operand were never called to begin with then prepend them from original name to there new name
                if operand1 not in assigned_vars:
                    if operand1.startswith("vr"):
                        if (f"{operand1} = {operand1.split('_')[0]};") not in to_prepend:
                            to_prepend.append(f"{operand1} = {operand1.split('_')[0]};")
                    if operand1.startswith("_new_name"):
                        if (f"{operand1} = {operand1.rpartition('_')[0]};") not in to_prepend:
                            to_prepend.append(f"{operand1} = {operand1.rpartition('_')[0]};")
                        
                if operand2 not in assigned_vars:
                    if operand2.startswith("vr"):
                        if (f"{operand2} = {operand2.split('_')[0]};") not in to_prepend:
                            to_prepend.append(f"{operand2} = {operand2.split('_')[0]};")
                    if operand2.startswith("_new_name"):
                        if (f"{operand2} = {operand2.rpartition('_')[0]};") not in to_prepend:
                            to_prepend.append(f"{operand2} = {operand2.rpartition('_')[0]};")

            # repeat for single operation
            elif match_single_operand:
                destination, operation, operand = match_single_operand.groups()
                assigned_vars.append(destination)


                if operand not in assigned_vars:
                    if operand.startswith("vr"):
                        if (f"{operand} = {operand.split('_')[0]};") not in to_prepend:
                            to_prepend.append(f"{operand} = {operand.split('_')[0]};")
                    if operand.startswith("_new_name"):
                        if (f"{operand} = {operand.rpartition('_')[0]};") not in to_prepend:
                            to_prepend.append(f"{operand} = {operand.rpartition('_')[0]};")

            # repeat for mastch statement
            elif match_assignment:
                left_var, right_var = match_assignment.groups()
                assigned_vars.append(left_var)

                if right_var not in assigned_vars:
                    if right_var.startswith("vr"):
                        if (f"{right_var} = {right_var.split('_')[0]};") not in to_prepend:
                            to_prepend.append(f"{right_var} = {right_var.split('_')[0]};")
                    if right_var.startswith("_new_name"):
                        if f"{right_var} = {right_var.rpartition('_')[0]};" not in to_prepend:
                            to_prepend.append(f"{right_var} = {right_var.rpartition('_')[0]};")
            # else:
            #     print(inst)
            #     new_block.append(inst)

        
        # next up is the processed set to stitch back at the end
        processed = set()
        postpend = []

        # using the above assigned var list reverse it to get the most recent assigned var (since they can be duplicate in the list
        for var in reversed(assigned_vars):
            # check the var is in processed or not then if not split and add to instruction list
            if var.startswith("vr"):
                if var.split('_')[0] not in processed:
                    processed.add(var.split('_')[0])
                    postpend.append(f"{var.split('_')[0]} = {var};")
            elif var.startswith("_new_name"):
                if var.rpartition('_')[0] not in processed:
                    processed.add(var.rpartition('_')[0])
                    postpend.append(f"{var.rpartition('_')[0]} = {var};")

        new_block += postpend
        new_block[:0] = to_prepend
        
        new_new_basic.append(new_block)
    new_program = [inst for block in new_new_basic for inst in block]
    return new_program, new_vars, edited_line
