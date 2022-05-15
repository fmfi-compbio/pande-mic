class PipelineState():

    def __init__(self, runner):
        self.runner = runner

    def switch(self, state):
        self.__class__ = state
        print("pipeline state: "+ state.name)
    
    def handle_interrupt(self):
        pass

class InitState(PipelineState):
    name = "init"

    def handle_interrupt(self):
        print("----------------------------------------------------")
        print("handling interrupt from init state (nothing special to do)")

class BatchingState(PipelineState):
    name = "batching"

    def handle_interrupt(self):
        print("----------------------------------------------------")
        print("handling interrupt from batching state, please wait")
        self.runner.clean_batches()

class SnakemakeState(PipelineState):
    name = "snakemake"

    def handle_interrupt(self):
        print("----------------------------------------------------")
        print("handling interrupt from snakemake state, please wait")
        print("batch folder: " +self.runner.batch_folder)
        print("not summarized: "+str(self.runner.not_summarized))
        #nothing special to do here (problems have to be solved in the snakemake pipeline - summarized files are renamed, indicator files are created..)
        #TODO: check whether summarized files are renamed consistently / whether a .merging file is present (and remove .summarized from those that are not, otherwise they will NOT be summarized in the next run)

class BatchCleaningState(PipelineState):
    name = "batch cleaning"

    def handle_interrupt(self):
        print("----------------------------------------------------")
        print("handling interrupt from batch cleaning state, please wait")
        self.runner.clean_batches() #remove links
        # everyhing else handled in snakemake
        
class WriteBatchesState(PipelineState):
    name = "write batches"

    def handle_interrupt(self):
        print("----------------------------------------------------")
        print("handling interrupt from write batches - sorry, this needs to be done, please wait, it won't take long")
        self.runner.write_batches()
