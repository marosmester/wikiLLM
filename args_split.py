std_args = ["parse=on", "path="]
std_args_split = []
for arg in std_args:
        if "=" in arg:
            temp = arg.split("=")
            std_args_split.append(temp[0]+"=")
            std_args_split.append(temp[1])
        else:
            std_args_split.append(arg)

print(std_args_split)