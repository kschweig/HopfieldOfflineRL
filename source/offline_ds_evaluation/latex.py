

def create_latex_table(path, arguments):

    environment = {"MiniGrid-LavaGapS7-v0": "lava", "MiniGrid-Dynamic-Obstacles-8x8-v0": "obstacles",
                   "CartPole-v1": "cartpole", "Acrobot-v1":"acrobot", "MountainCar-v0": "mountaincar",
                   "Breakout-MinAtar-v0": "breakout", "Space_invaders-MinAtar-v0": "spaceinvaders"}
    buffer = {"er": "Exp. Replay", "fully": "Final Policy", "random": "Random Policy",
              "mixed": "Mixed Policy", "noisy": "Noisy Policy"}
    results = ["Return", "Return (Norm.)", "Entropy (Norm.)", "Sparsity", "Episode Length",
               "Unique States / Ep.", "Uniqueness", "Unique States"]

    with open(path, "w") as f:
        f.write("\\begin{table}[h]\n\\centering\n\\begin{tabular}{l|" + "c"*len(arguments) + "}\n")

        f.write("Metric  \\hspace{2pt} \\symbol{92} \\hspace{2pt} Buffer Type")
        for i in range(len(arguments)):
            f.write(" & " + buffer[arguments[i][1]])
        f.write(" \\\\ \\hline \n")

        for j in range(2, len(arguments[0])):
            f.write(results[j-2] + " & ")
            for i in range(len(arguments)):
                if isinstance(arguments[i][j], tuple):
                    f.write(f"${round(arguments[i][j][0], 2):.2f} \\pm {round(arguments[i][j][1], 2):.2f}$")
                else:
                    f.write(f"${round(arguments[i][j], 5)}$")
                if i == len(arguments) - 1:
                    f.write("\\\\ \n")
                else:
                    f.write(" & ")

        f.write("\\end{tabular}\n\\caption{Dataset evaluation metrics for all buffer types of environment '"
                +arguments[0][0]+"'.}\n")
        f.write("\\label{tab:ds_eval_"+environment[arguments[0][0]]+"}\n\\end{table}")