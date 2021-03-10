import ANNarchy

class LeakyRate (ANNarchy.Population):

    def __init__(self, size, tau):

        self.size = size

        self.tau = ANNarchy.Value(self, tau)

        self.r = ANNarchy.Vector(self, min=0.0)

        super(self, LeakyRate).__init__(size)

    def step(self):

        self.r.update("tau * dv/dt  + v = g_exc * (v - v_Exc) + g_inh*(v-V_inh) + I", method="euler")
        self.rmax.update("rmax = max(r)")

        with ConcurrentEvaluation():
            ANNarchy.diff(self.r, (sum(exc) - r)/self.tau)
            ANNarchy.diff(self.w, (r - w)/self.tau)

        ANNarchy.eq(self.w, r)


class Hebb(ANNarchy.Projection):

    def __init__(self, pre, post):

        self.connectivity = ANNarchy.SparseConnectivity()
        self.connectivity = ANNarchy.ConvolutionConnectivity()

        self.w = ANNarchy.Matrix(self.connectivity)

        self.alpha = ANNarchy.Vector(self.connectivity, post=True)
        self.beta = ANNarchy.Matrix(self.connectivity)


    def step():

        self.transmit_on_pre("w") # spikes
        self.transmit("w*pre.r")

        self.w.update(inc="pre.r * post.r")
        self.w.update(eq="pre.r * post.r")
        self.w.update(deq="pre.r * post.r")

    def on_pre():

        self.w.update()

    def on_post():

    def update():

        self.w = 0.0

proj = net.connect(pop, pop, Hebb)

proj.connectivity.fill()

class EInet (ANNarchy.Area):

    def __init__(self):

        super(self, EInet).__init__()

    def build(self):

        self.E = self.add(LeakyRate(100, tau=20.0))
        self.I = self.add(LeakyRate(20, tau=20.0))

        self.proj = connect(self.E, self.I)


class Net(ANNarchy.Network):

    def __init__(self):

    def build(self):

        self.pop = self.add(LeakyRate(100, Izhikevich))

    @numba
    def step(self):

        # Inputs
        img = cv2.load_image(ejje)
        inp.r = img

        pop.perturbation = np.random.uniform()

        # Wrighted sums
        self.projections().collect()

        self.record(self.proj.get("exc"))

        # Pre.synaptic spike

        # Neural updates
        self.populations().update()
        # oder:
        with async():
            self.pop.update(nb_threads=2)
            self.pop2.update2()

        # Spike propagation
        self.populations().emit_spikes()

        # Synaptic variable updates
        r_mean = np.mean(pop.r)

        if r_mean > 0.5:    
            self.proj.update()
        else:
            stop()

        # Post-synaptic spike

        # Record
        self.record(self.pop.r)

        if self.step %% 10000 = 0:
            self.proj.prune()

    def trial(self):

        self.inp.r = ...

        for t in range(100):
            self.step2()


net = ANNarchy.Network()

net.compile({
    'paradigm': "openmp"
    'nb_threads': 4,
    'processes': [
        area1,
        area2,
        pop3
    ]
})

net.simulate(1000., method=Net.step)

net.save()

net.simulate(1000., method=Net.step2)