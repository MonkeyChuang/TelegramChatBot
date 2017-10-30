from transitions import Machine
import numpy as np

class AngerMeasure(Machine):
    T_0 = np.array([
            [ .60 , .27 , .08 , .04 , .01 , .0 , .0 , .0 ],
            [ .15 , .4 , .25 , .12 , .06 , .02 , .0 , .0 ],
            [ .0 , .1 , .28 , .3 , .17 , .1 , .05 , .0 ],
            [ .0 , .0 , .03 , .15 , .45 , .2 , .1 , .07],
            [ .0 , .0 , .0 , .01 , .09 , .5 , .25 , .15 ],
            [ .0 , .0 , .0 , .0 , .0 , .07 , .43 , .5 ],
            [ .0 , .0 , .0 , .0 , .0 , .0 , .05 , .95 ],
            [ .27 , .35 , .21 , .1 , .06 , .009 , .001 , .0 ]])
    T_1 = np.array([
            [ .5 , .5 , .0 , .0 , .0 , .0 , .0 ],
            [ .0 , .4 , .6 , .0 , .0 , .0 , .0 ],
            [ .0 , .0 , .35 , .65 , .0 , .0 , .0  ],
            [ .0 , .0 , .0 , .2 , .8 , .0 , .0 ],
            [ .0 , .0 , .0 , .0 , .1 , .9 , .0 ],
            [ .0 , .0 , .0 , .0 , .0 , .01 , .99 ],
            [ .06 , .2 , .35 , .3 , .07 , .02 , .0 ]])
    Trans = [T_0,T_1]
    def __init__(self):
        
        """
        @Type 0
        E[第一次到max Lv.] = 8
        分佈:左低右高，分散
        機器人種類:溫和。偶爾性情不定。
        
        @Type 1        
        E[第一次到max Lv.] = 8
        分佈:左低右高，集中
        機器人種類:溫和。很有規則的機器人，生氣的時機都差不多
        """
        self.T=self.Trans[1]

        self.states=[
            {'name':'0'}
        ]
        Machine.__init__(self,states=self.states,initial='0')
        other_states = list(map(str,range(1,self.T.shape[0])))
        self.add_states(other_states)
        self.max_lv = self.T.shape[0]-1

    def nextLevel(self):
        now_state = int(self.state)
        new_state = int()
        cum_prob_list = np.cumsum(self.T[now_state])
        p = np.random.uniform(0,1)
        for index in range(0,self.max_lv+1):
            if p < cum_prob_list[index]:
                #print(cum_prob_list)
                #print('p={}'.format(p))
                new_state = index
                return new_state
    def resetLevel(self):
        #print('reset to state 0')
        self.to_0()
    def gotAnnoyed(self):
        now_state = int(self.state)
        if now_state != self.max_lv:
            new_state = self.nextLevel()
            print('now_state={}'.format(now_state))
            print('new_state={}'.format(new_state))            
            func_name = 'to_'+str(new_state)
            to_state = getattr(self,func_name)
            to_state()
        else:
            print('cannot get annoyed anymore!')
    def afterFlareUp(self):
        now_state = int(self.state)
        if now_state == self.max_lv:
            new_state = self.nextLevel()
            print('after .now_state={}'.format(now_state))
            print('after .new_state={}'.format(new_state))            
            func_name = 'to_'+str(new_state)
            to_state = getattr(self,func_name)
            to_state()
        else:
            print("I haven't flared up yet ")
    def gotSatisfied(self):
        now_state = int(self.state)
        new_state = now_state-1 if now_state>=1 else 0
        print('back .now_state={}'.format(now_state))
        print('back .new_state={}'.format(new_state))        
        func_name = 'to_'+str(new_state)
        to_state = getattr(self,func_name)
        to_state()       
    def flareUp(self):
        now_state = int(self.state)
        return True if now_state == self.max_lv else False

machine=AngerMeasure() 
print(machine.T)
#machine.get_graph().draw('fsm.png',prog='dot')
#machine.gotAnnoyed()
#machine.gotAnnoyed()