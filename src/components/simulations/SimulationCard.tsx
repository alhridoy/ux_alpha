
import React from 'react';
import { Clock, CheckCircle, XCircle, BarChart2, MessageSquare } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { SimulationResult } from '@/types';
import { formatDistanceToNow } from 'date-fns';

type SimulationCardProps = {
  simulation: SimulationResult;
  onClick: () => void;
};

const SimulationCard = ({ simulation, onClick }: SimulationCardProps) => {
  const formattedTime = formatDistanceToNow(simulation.timestamp, { addSuffix: true });
  
  return (
    <Card className="hover:border-uxagent-purple transition-colors cursor-pointer" onClick={onClick}>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <div className="flex items-start gap-3">
            <div className="h-10 w-10 rounded-full overflow-hidden flex-shrink-0">
              <img 
                src={`${simulation.persona.profileImage}?w=80&h=80&fit=crop&crop=faces&auto=format`}
                alt={simulation.persona.name}
                className="h-full w-full object-cover" 
              />
            </div>
            <div>
              <CardTitle className="text-base">{simulation.persona.name}</CardTitle>
              <p className="text-muted-foreground text-xs">
                {simulation.persona.age} y/o {simulation.persona.occupation}
              </p>
            </div>
          </div>
          <Badge variant={simulation.taskCompleted ? "default" : "destructive"} className={simulation.taskCompleted ? "bg-green-500 hover:bg-green-600" : ""}>
            {simulation.taskCompleted ? (
              <CheckCircle className="h-3 w-3 mr-1" />
            ) : (
              <XCircle className="h-3 w-3 mr-1" />
            )}
            {simulation.taskCompleted ? "Completed" : "Incomplete"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="pb-2">
        <p className="mb-2 line-clamp-2 text-sm font-medium">"{simulation.task}"</p>
        <div className="text-sm text-muted-foreground truncate">
          <span className="inline-block">{new URL(simulation.webUrl).hostname}</span>
        </div>
        <div className="flex items-center mt-2 text-xs text-muted-foreground">
          <Clock className="h-3 w-3 mr-1" />
          <span>{simulation.durationSeconds}s duration</span>
          <span className="mx-2">•</span>
          <span>{simulation.actions.length} actions</span>
        </div>
      </CardContent>
      <CardFooter className="pt-2 border-t flex justify-between">
        <div className="text-xs text-muted-foreground">{formattedTime}</div>
        <div className="flex gap-1">
          <Button variant="ghost" size="sm" className="h-7 px-2">
            <BarChart2 className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="sm" className="h-7 px-2">
            <MessageSquare className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
};

export default SimulationCard;
