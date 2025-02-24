from getdist import plots, MCSamples


class BaseSampler:
    def __init__(self):
        pass

    def plot_triangle(self, save_fn=None, thin=1, add_bestfit=False, **kwargs):
        """Plot triangle plot
        """
        import matplotlib.pyplot as plt
        names = [param for param in self.priors.keys() if param not in self.fixed_parameters]
        labels = [self.labels[param].strip('$') for param in names]
        data = self.get_chain(flat=True, thin=thin)
        samples = MCSamples(samples=data['samples'], weights=data['weights'], names=names,
                            loglikes=data['log_likelihood'], labels=labels, ranges=self.ranges)
        g = plots.get_subplot_plotter()
        g.triangle_plot(samples, **kwargs)
        maxl = data['samples'][data['log_likelihood'].argmax()]
        if add_bestfit:
            print('Adding bestfit')
            print(maxl)
            params = kwargs['params'] if 'params' in kwargs else names
            ndim = len(params)
            finished = []
            ax_idx = 0
            for i, param1 in enumerate(params):
                for j, param2 in enumerate(params[::-1]):
                    if param2 in finished: continue
                    if param1 != param2:
                        g.fig.axes[ax_idx].plot(maxl[names.index(param1)], maxl[names.index(param2)],
                                                marker='*', ms=10.0, color='k', mew=1.0, mfc='w')
                    ax_idx += 1
                finished.append(param1)
        if save_fn:
            plt.savefig(save_fn, bbox_inches='tight')
        plt.show()
    
    def plot_bestfit(self, save_fn=None, thin=1, model='mean'):
        import matplotlib.pyplot as plt
        chain = self.get_chain(flat=True, thin=thin)
        maxl = chain['samples'][chain['log_likelihood'].argmax()]
        mean = chain['samples'].mean(axis=0)
        theta = self.fill_params(mean) if model == 'mean' else self.fill_params(maxl)
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.plot(self.observation, marker='o', ms=3.0, ls='', label='data')
        ax.plot(self.get_model_prediction(theta), label='model')
        ax.set_xlabel('bin number', fontsize=15)
        ax.set_ylabel(r'$X$', fontsize=15)
        ax.legend()
        plt.tight_layout()
        if save_fn:
            self.logger.info(f'Saving {save_fn}')
            plt.savefig(save_fn, bbox_inches='tight')
        plt.show()


    def plot_trace(self, save_fn=None, thin=1):
        """Parameter trace plot
        """
        import matplotlib.pyplot as plt
        names = [param for param in self.priors.keys() if param not in self.fixed_parameters]
        labels = [self.labels[param] for param in names]
        data = self.get_chain(flat=True, thin=thin)
        fig, ax = plt.subplots(len(names), 1, figsize=(10, 2*len(names)))
        for i, name in enumerate(names):
            ax[i].plot(data['samples'][:, i])
            ax[i].set_ylabel(labels[i])
        ax[i].set_xlabel('Iteration')
        plt.tight_layout()
        if save_fn:
            self.logger.info(f'Saving {save_fn}')
            plt.savefig(save_fn, bbox_inches='tight')
        plt.show()

    def save_chain(self, save_fn, metadata=None):
        """Save the chain to a file
        """
        import numpy as np
        data = self.get_chain(flat=True)
        names = [param for param in self.priors.keys() if param not in self.fixed_parameters]
        cout = {**data,
            'ranges': self.ranges,
            'names': names,
            'labels': self.labels,
        }
        if metadata:
            for key, val in metadata.items():
                cout[key] = val
        self.logger.info(f'Saving {save_fn}')
        np.save(save_fn, cout)

    def save_table(self, save_fn):
        from tabulate import tabulate
        chain = self.get_chain(flat=True)
        maxl = chain['samples'][chain['log_likelihood'].argmax()]
        mean = chain['samples'].mean(axis=0)
        std = chain['samples'].std(axis=0)
        names = [param for param in self.priors.keys() if param not in self.fixed_parameters]
        headers = ['parameter', 'max-like', 'mean', 'std']
        table = []
        for i, name in enumerate(names):
            table.append([name, f"{maxl[i]:.4f}", f"{mean[i]:4f}", f"{std[i]:.4f}"])
        with open(save_fn, 'w') as f:
            self.logger.info(f'Saving {save_fn}')
            f.write(tabulate(table, tablefmt='pretty', headers=headers))
