from shiny import App, ui, render, reactive
import matplotlib.pyplot as plt
import numpy as np
import copy

from model.results import run_model
from model.inputs import PlantInputs
from model.scenarios import SCENARIOS


###############################################################
# UI
###############################################################

app_ui = ui.page_sidebar(

    ###########################################################
    # Sidebar
    ###########################################################

    ui.sidebar(

        ui.h3("Scenario"),

        ui.input_select(
            "scenario",
            "Scenario",
            choices=list(SCENARIOS.keys())
        ),

        ui.hr(),

        #########################
        # Brine
        #########################

        ui.h4("Brine"),

        ui.input_numeric(
            "feed_flow_m3h",
            "Feed Flow (m³/h)",
            value=15
        ),

        ui.input_numeric(
            "feed_li_gL",
            "Lithium (g/L)",
            value=1.5
        ),

        ui.input_numeric(
            "feed_mg_gL",
            "Magnesium (g/L)",
            value=.2
        ),

        #########################
        # Electrochemistry
        #########################

        ui.h4("Electrochemical Stack"),

        ui.input_numeric(
            "current_density_A_m2",
            "Current Density (A/m²)",
            value=250
        ),

        ui.input_numeric(
            "electrode_area_m2_per_stack",
            "Electrode Area / Stack (m²)",
            value=8
        ),

        ui.input_numeric(
            "installed_stacks",
            "Installed Stacks",
            value=120
        ),

        ui.input_slider(
            "active_stack_fraction",
            "Active Stack Fraction",
            min=0,
            max=1,
            value=.9
        ),

        ui.input_slider(
            "faradaic_efficiency",
            "Faradaic Efficiency",
            min=0,
            max=1,
            value=.92
        ),

        #########################
        # Economics
        #########################

        ui.h4("Economics"),

        ui.input_numeric(
            "electricity_price_per_MWh",
            "Electricity Price ($/MWh)",
            value=40
        ),

        width=350
    ),

    ###########################################################
    # Tabs
    ###########################################################

    ui.navset_card_tab(

        ui.nav_panel(
            "Process Competitiveness",
            ui.output_ui("competitiveness")
        ),

        ui.nav_panel(
            "Engineering Metrics",
            ui.output_ui("engineering")
        ),

        ui.nav_panel(
            "Plant Design Summary",
            ui.output_ui("design")
        ),

        ui.nav_panel(
            "Mass Balance Check",
            ui.output_ui("massbalance")
        ),

        ui.nav_panel(
            "Process Insights",

            ui.output_plot("opex_plot"),
            ui.output_plot("li_plot")
        ),

        ui.nav_panel(
            "Sensitivity Analysis",

            ui.output_plot("current_density_plot"),
            ui.output_plot("stack_plot")
        ),

        ui.nav_panel(
            "Process Operating Envelope",

            ui.output_plot("heatmap")
        )
    )
)


###############################################################
# SERVER
###############################################################

def server(input, output, session):


    ###########################################################
    # Scenario defaults
    ###########################################################

    @reactive.calc
    def scenario():

        return SCENARIOS[input.scenario()]()


    ###########################################################
    # Update sidebar when scenario changes
    ###########################################################

    @reactive.effect
    def _():

        s = scenario()

        ui.update_numeric(
            "feed_flow_m3h",
            value=s.feed_flow_m3h,
            session=session
        )

        ui.update_numeric(
            "feed_li_gL",
            value=s.feed_li_gL,
            session=session
        )

        ui.update_numeric(
            "feed_mg_gL",
            value=s.feed_mg_gL,
            session=session
        )

        ui.update_numeric(
            "current_density_A_m2",
            value=s.current_density_A_m2,
            session=session
        )

        ui.update_numeric(
            "electrode_area_m2_per_stack",
            value=s.electrode_area_m2_per_stack,
            session=session
        )

        ui.update_numeric(
            "installed_stacks",
            value=s.installed_stacks,
            session=session
        )

        ui.update_slider(
            "active_stack_fraction",
            value=s.active_stack_fraction,
            session=session
        )

        ui.update_slider(
            "faradaic_efficiency",
            value=s.faradaic_efficiency,
            session=session
        )

        ui.update_numeric(
            "electricity_price_per_MWh",
            value=s.electricity_price_per_MWh,
            session=session
        )


    ###########################################################
    # Build PlantInputs
    ###########################################################

    @reactive.calc
    def params():

        s = scenario()

        return PlantInputs(

            #################################
            # USER EDITABLE
            #################################

            feed_flow_m3h=input.feed_flow_m3h(),
            feed_li_gL=input.feed_li_gL(),
            feed_mg_gL=input.feed_mg_gL(),

            current_density_A_m2=
                input.current_density_A_m2(),

            electrode_area_m2_per_stack=
                input.electrode_area_m2_per_stack(),

            installed_stacks=
                input.installed_stacks(),

            active_stack_fraction=
                input.active_stack_fraction(),

            faradaic_efficiency=
                input.faradaic_efficiency(),

            electricity_price_per_MWh=
                input.electricity_price_per_MWh(),

            #################################
            # Scenario defaults
            #################################

            feed_na_gL=s.feed_na_gL,
            feed_k_gL=s.feed_k_gL,
            feed_ca_gL=s.feed_ca_gL,

            stack_recovery=s.stack_recovery,
            polishing_recovery=s.polishing_recovery,
            pretreatment_recovery=s.pretreatment_recovery,
            product_recovery=s.product_recovery,

            thermodynamic_voltage_V=s.thermodynamic_voltage_V,
            area_specific_resistance_ohm_m2=s.area_specific_resistance_ohm_m2,
            limiting_current_density_A_m2=s.limiting_current_density_A_m2,
            activation_coeff_V=s.activation_coeff_V,

            uptime_fraction=s.uptime_fraction,
            purge_fraction=s.purge_fraction,
            recycle_ratio=s.recycle_ratio,

            years_on_stream=s.years_on_stream,
            asr_growth_per_year=s.asr_growth_per_year,
            fe_fade_per_year=s.fe_fade_per_year,

            stack_replacement_interval_years=
                s.stack_replacement_interval_years,

            stack_replacement_cost_per_stack_per_year=
                s.stack_replacement_cost_per_stack_per_year,

            fixed_opex_per_year=s.fixed_opex_per_year,

            capex_base_usd=s.capex_base_usd,
            capex_reference_tpy=s.capex_reference_tpy,
            capex_scaling_exponent=s.capex_scaling_exponent
        )


    @reactive.calc
    def r():
        return run_model(params())


###############################################################
# Process competitiveness
###############################################################

    @output
    @render.ui
    def competitiveness():

        x=r()

        return ui.layout_columns(

            ui.value_box(
                "Energy Intensity",
                f"{x['sec_kwh_per_kg']:.2f} kWh/kg"
            ),

            ui.value_box(
                "Lithium Recovery",
                f"{100*x['overall_recovery']:.1f}%"
            ),

            ui.value_box(
                "Operating Cost",
                f"${x['opex_usd_per_ton']:.0f}/t"
            ),

            ui.value_box(
                "Annual Production",
                f"{x['annual_tpy']:.0f} t/y"
            )
        )


###############################################################
# Engineering
###############################################################

    @output
    @render.ui
    def engineering():

        x=r()
        p=params()

        return ui.layout_columns(

            ui.value_box(
                "Current / Stack",
                f"{x['total_current_A']/x['active_stacks']:.0f} A"
            ),

            ui.value_box(
                "Power / Stack",
                f"{x['power_kW']/x['active_stacks']:.2f} kW"
            ),

            ui.value_box(
                "Flow / Active Stack",
                f"{p.feed_flow_m3h/x['active_stacks']:.2f}"
            ),

            ui.value_box(
                "Brine Intensity",
                f"{p.feed_flow_m3h/max(x['annual_tpy'],1):.4f}"
            )
        )


###############################################################
# Plant design
###############################################################

    @output
    @render.ui
    def design():

        x=r()
        p=params()

        total_area=(
            p.installed_stacks*
            p.electrode_area_m2_per_stack
        )

        return ui.layout_columns(

            ui.value_box(
                "Installed Stacks",
                p.installed_stacks
            ),

            ui.value_box(
                "Total Electrode Area",
                f"{total_area:.0f} m²"
            ),

            ui.value_box(
                "Plant Power",
                f"{x['power_kW']:.0f} kW"
            ),

            ui.value_box(
                "Annual Brine Throughput",
                f"{8760*p.feed_flow_m3h:.0f}"
            ),

            ui.value_box(
                "Electricity Cost/t",
                f"${x['electricity_cost_usd_per_year']/x['annual_tpy']:.0f}"
            ),

            ui.value_box(
                "Replacement Cost/t",
                f"${x['replacement_cost_usd_per_year']/x['annual_tpy']:.0f}"
            )
        )


###############################################################
# Mass balance
###############################################################

    @output
    @render.ui
    def massbalance():

        x=r()

        li_in=x["feed"]["Li_kgph"]

        li_accounted=(
            x["product"]["Li_kgph_product"]
            + x["product"]["Li_kgph_recycle"]
            + x["product"]["Li_kgph_purge_loss"]
        )

        err=li_in-li_accounted

        return ui.layout_columns(

            ui.value_box(
                "Lithium In",
                f"{li_in:.2f}"
            ),

            ui.value_box(
                "Lithium Accounted",
                f"{li_accounted:.2f}"
            ),

            ui.value_box(
                "Balance Error",
                f"{err:.4f}"
            )
        )


###############################################################
# Process insights
###############################################################

    @output
    @render.plot
    def opex_plot():

        x=r()

        vals=[
            x["electricity_cost_usd_per_year"]/x["annual_tpy"],
            x["replacement_cost_usd_per_year"]/x["annual_tpy"],
            x["opex_usd_per_ton"]
        ]

        plt.figure()
        plt.bar(
            ["Electricity",
             "Replacement",
             "Total OPEX"],
            vals
        )


    @output
    @render.plot
    def li_plot():

        x=r()

        vals=[

            x["pretreated"]["Li_kgph"],
            x["polished"]["Li_kgph_polished"],
            x["product"]["Li_kgph_purge_loss"],
            x["product"]["Li_kgph_recycle"],
            x["product"]["Li_kgph_product"]
        ]

        plt.figure()

        plt.bar(
            ["Pretreat",
             "Polished",
             "Purge",
             "Recycle",
             "Product"],
            vals
        )


###############################################################
# Sensitivity
###############################################################

    @output
    @render.plot
    def current_density_plot():

        p=params()

        xs=np.linspace(50,500,30)
        ys=[]

        for x in xs:

            q=copy.deepcopy(p)
            q.current_density_A_m2=x

            ys.append(
                run_model(q)["sec_kwh_per_kg"]
            )

        plt.figure()
        plt.plot(xs,ys)
        plt.xlabel("Current Density")
        plt.ylabel("Energy Intensity")


    @output
    @render.plot
    def stack_plot():

        p=params()

        xs=np.arange(20,300,10)
        ys=[]

        for n in xs:

            q=copy.deepcopy(p)
            q.installed_stacks=n

            ys.append(
                run_model(q)["annual_tpy"]
            )

        plt.figure()
        plt.plot(xs,ys)
        plt.xlabel("Installed stacks")
        plt.ylabel("Annual production")


###############################################################
# Heatmap
###############################################################

    @output
    @render.plot
    def heatmap():

        p=params()

        current=np.linspace(50,500,25)
        stacks=np.linspace(20,300,25)

        z=np.zeros((25,25))

        for i,j in enumerate(current):

            for k,n in enumerate(stacks):

                q=copy.deepcopy(p)

                q.current_density_A_m2=j
                q.installed_stacks=int(n)

                z[k,i]=run_model(q)["annual_tpy"]

        plt.figure()

        plt.imshow(
            z,
            origin="lower",
            aspect="auto"
        )

        plt.colorbar(
            label="Annual Production"
        )

        plt.xlabel(
            "Current Density"
        )

        plt.ylabel(
            "Installed Stacks"
        )


app = App(app_ui, server)