import math

import pandas as pd


class transistor(object):
    def __init__(self, df, idx):
        self.df = df
        self.idx = idx
        self.mpn = self.df.loc[self.idx]['mpn']
        self.r_ds_on = self.df.loc[self.idx]['r_ds_on']
        self.c_oss = self.df.loc[self.idx]['c_oss']
        self.v_c_oss = self.df.loc[self.idx]['c_oss@V']
        self.q_g = self.df.loc[self.idx]['q_g']
        self.q_rr = self.df.loc[self.idx]['q_rr']
        self.tr = self.df.loc[self.idx]['time_rise']
        self.tf = self.df.loc[self.idx]['time_fall']


class workbench(object):
    def __init__(self, voltage, current, duty, frequency, transistor=None, ):
        self.I = current
        self.V = voltage
        self.D = duty
        self.f = frequency
        self.Q = transistor

        dict = {"current": self.I}
        self.out = pd.DataFrame(columns=["conduction", "switching", "reverse recovery", "output charge", "gate charge"])

    sweep_start = None
    sweep_stop = None
    sweep_lst = None

    def solder_transistor(self, transistor):
        self.Q = transistor
        return transistor.mpn

    def set_sweep_range(self, start, stop):
        self.sweep_start = start
        self.sweep_stop = stop
        if start > stop:
            self.sweep_start = stop
            self.sweep_stop = start
        self.sweep_lst = [int(i) for i in range(self.sweep_start, self.sweep_stop)]

    def set_sweep_list(self, lst):
        self.sweep_lst = lst

    def frequency_sweep(self):
        if self.sweep_start or self.sweep_stop or self.sweep_lst is None:
            print("Set frequency sweep range first")
        else:
            methods = [
                self.return_value,
                self.loss_conduction,
                self.loss_switching,
                self.loss_output_charge,
                self.loss_gate_charge,
                self.loss_reverse_recovery,
                self.loss_total
            ]
            lst = [[method(f=frequency) for method in methods] for frequency in self.sweep_lst]
            df = pd.DataFrame(lst, columns=[
                "frequency",
                "conduction",
                "switching",
                "output charge",
                "gate charge",
                "reverse recovery",
                "total"
            ])
            df.attrs = {
                "part": self.Q.mpn,
                "current": self.I,
                "voltage": self.V,
                "duty": self.D,
                "frequency": None
            }
            return df

    def current_sweep(self):
        if self.sweep_start or self.sweep_stop or self.sweep_lst is None:
            print("Set current sweep range first")
        else:
            methods = [
                self.return_value,
                self.loss_conduction,
                self.loss_switching,
                self.loss_output_charge,
                self.loss_gate_charge,
                self.loss_reverse_recovery,
                self.loss_total
            ]
            lst = [[method(I=current) for method in methods] for current in self.sweep_lst]
            df = pd.DataFrame(lst, columns=[
                "current",
                "conduction",
                "switching",
                "output charge",
                "gate charge",
                "reverse recovery",
                "total"
            ])
            df.attrs = {
                "part": self.Q.mpn,
                "current": None,
                "voltage": self.V,
                "duty": self.D,
                "frequency": self.f
            }
            return df

    def duty_sweep(self):
        self.sweep_lst = [i*0.01 for i in range(100)]
        methods = [
            self.return_value,
            self.loss_conduction,
            self.loss_switching,
            self.loss_output_charge,
            self.loss_gate_charge,
            self.loss_reverse_recovery,
            self.loss_total
        ]
        lst = [[method(D=duty) for method in methods] for duty in self.sweep_lst]
        df = pd.DataFrame(lst, columns=[
            "duty",
            "conduction",
            "switching",
            "output charge",
            "gate charge",
            "reverse recovery",
            "total"
        ])
        df.attrs = {
            "part": self.Q.mpn,
            "current": self.I,
            "voltage": self.V,
            "duty": None,
            "frequency": self.f
        }
        return df

    def loss_conduction(self, I=None, V=None, D=None, f=None):
        [local_I, local_V, local_D, local_f] = self.overwrite_local(I, V, D, f)
        return local_I ** 2 * self.Q.r_ds_on * local_D

    def loss_switching(self, I=None, V=None, D=None, f=None):
        [local_I, local_V, local_D, local_f] = self.overwrite_local(I, V, D, f)
        return 0.5 * local_V * local_I * (self.Q.tr + self.Q.tf) * local_f

    def loss_reverse_recovery(self, I=None, V=None, D=None, f=None):
        [local_I, local_V, local_D, local_f] = self.overwrite_local(I, V, D, f)
        return local_V * self.Q.q_rr * local_f

    def loss_output_charge(self, I=None, V=None, D=None, f=None):
        [local_I, local_V, local_D, local_f] = self.overwrite_local(I, V, D, f)
        return 0.5 * self.Q.c_oss * math.sqrt(self.Q.v_c_oss / local_V) * local_V ** 2 * local_f

    def loss_gate_charge(self, I=None, V=None, D=None, f=None):
        [local_I, local_V, local_D, local_f] = self.overwrite_local(I, V, D, f)
        return self.Q.q_g * local_V * local_f

    def loss_total(self, I=None, V=None, D=None, f=None):
        return (
                self.loss_conduction(I, V, D, f) +
                self.loss_switching(I, V, D, f) +
                self.loss_gate_charge(I, V, D, f) +
                self.loss_output_charge(I, V, D, f) +
                self.loss_reverse_recovery(I, V, D, f)
        )

    def return_value(self, I=None, V=None, D=None, f=None):
        if I is not None:
            return I
        if V is not None:
            return V
        if D is not None:
            return D
        if f is not None:
            return f
        return 0

    def overwrite_local(self, I, V, D, f):
        if I is None:
            local_I = self.I
        else:
            local_I = I
        if V is None:
            local_V = self.V
        else:
            local_V = V
        if D is None:
            local_D = self.D
        else:
            local_D = D
        if f is None:
            local_f = self.f
        else:
            local_f = f
        return [local_I, local_V, local_D, local_f]
