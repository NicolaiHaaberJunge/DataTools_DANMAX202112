"""
Interactive plotting
"""

import ipywidgets as widgets
import matplotlib.pyplot as plt


import ipywidgets as widgets

def plot(df):

    ### WIDGET DEFINITIONS ###

    valid_cols = [col for col in df.columns.to_list() if isinstance(df[col][0], (float, int))]
    
    ycols = valid_cols[1::]
    xcols = valid_cols

    output = widgets.Output()

    dropdown_left = widgets.Select(
        options=ycols,
        description='Left Y-Axis',
        disabled=False,
        layout=widgets.Layout(height="200px")

    )


    dropdown_right = widgets.Select(
        options=ycols,
        description='Right Y-Axis',
        disabled=False,
        layout=widgets.Layout(height="200px")
    )


    dropdown_xaxis = widgets.Select(
        options=xcols,
        description='X-Axis',
        disabled=False,
        layout=widgets.Layout(height="200px", margin="1000px 1000px 1000px 1000px 1000px")
    )


    logYLeft = widgets.Checkbox(
        description='Logarithmic',
        disabled=False,
    )

    logYRigth = widgets.Checkbox(
        description='Logarithmic',
        disabled=False,
    )


    with output:
        fig_spec, axL = plt.subplots(figsize=[8, 5])

        df.plot(x=dropdown_xaxis.value, y=dropdown_left.value, ax=axL, c="b", legend=False)
        lineLeft = axL.get_lines()[0]
        axL.set_ylabel(dropdown_left.value)
        axL.spines['left'].set_color('blue')
        axL.yaxis.label.set_color('blue')
        axL.tick_params(axis='y', colors='blue')

        axR = axL.twinx()
        
        axR.spines['right'].set_color('red')
        axR.yaxis.label.set_color('red')
        axR.tick_params(axis='y', colors='red')

        df.plot(x=dropdown_xaxis.value, y=dropdown_left.value, ax=axR, c="r", legend=False)
        lineRight = axR.get_lines()[0]
        axR.set_ylabel(dropdown_left.value)

    ### INTERACTION ###   

    def on_leftY_change(change):

        new_value = change['new']
        new_ys = df[new_value].to_numpy()
        lineLeft.set_ydata(new_ys)
        axL.set_ylabel(new_value)
        axL.relim()
        axL.autoscale_view(True,True,True)

    def on_rightY_change(change):

        new_value = change['new']
        new_ys = df[new_value].to_numpy()
        lineRight.set_ydata(new_ys)
        axR.set_ylabel(new_value)
        axR.relim()
        axR.autoscale_view(True,True,True)

    def on_Xaxis_change(change):
        new_value = change['new']
        new_xs = df[new_value].to_numpy()

        lineLeft.set_data(new_xs, lineLeft.get_ydata())
        lineRight.set_data(new_xs, lineRight.get_ydata())
        
        axL.relim()
        axL.autoscale_view(True,True,True)
        axL.set_xlabel(new_value)
        
        axR.relim()
        axR.autoscale_view(True,True,True)


    def on_logY_Left(change):
        if change['new']:
            axL.set_yscale("log")
        else:
            axL.set_yscale("linear")

    def on_logY_Right(change):
        if change['new']:
            axR.set_yscale("log")
        else:
            axR.set_yscale("linear")


    dropdown_left.observe(on_leftY_change, names='value')
    dropdown_right.observe(on_rightY_change, names='value')
    dropdown_xaxis.observe(on_Xaxis_change, names='value')
    
    logYLeft.observe(on_logY_Left, names='value')
    logYRigth.observe(on_logY_Right, names='value')
    
    
    ### LAYOUT ###

    left_side = widgets.VBox([dropdown_left, logYLeft, dropdown_xaxis])
    right_side = widgets.VBox([dropdown_right, logYRigth])
    main = widgets.HBox([left_side, output, right_side])

    return main