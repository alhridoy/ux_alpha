
import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  BarChart3,
  Home,
  UserRound,
  GanttChartSquare,
  MessageSquare,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const Header: React.FC = () => {
  return (
    <header className="border-b bg-white">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-gradient-to-r from-uxagent-purple to-uxagent-dark-purple p-2 text-white">
            <BarChart3 className="h-5 w-5" />
          </div>
          <Link to="/" className="text-xl font-bold text-uxagent-charcoal">
            UXAgent
          </Link>
        </div>
        
        <nav className="flex items-center space-x-1">
          <NavItem to="/" icon={<Home className="h-4 w-4 mr-2" />} label="Dashboard" />
          <NavItem to="/personas" icon={<UserRound className="h-4 w-4 mr-2" />} label="Personas" />
          <NavItem to="/simulations" icon={<GanttChartSquare className="h-4 w-4 mr-2" />} label="Simulations" />
          <NavItem to="/interviews" icon={<MessageSquare className="h-4 w-4 mr-2" />} label="Interviews" />
        </nav>
      </div>
    </header>
  );
};

interface NavItemProps {
  to: string;
  icon: React.ReactNode;
  label: string;
}

const NavItem: React.FC<NavItemProps> = ({ to, icon, label }) => {
  const isActive = window.location.pathname === to;
  
  return (
    <Button
      variant="ghost"
      className={cn(
        "flex items-center px-3 py-2",
        isActive && "bg-uxagent-light-purple text-uxagent-dark-purple"
      )}
      asChild
    >
      <Link to={to}>
        {icon}
        {label}
      </Link>
    </Button>
  );
};

export default Header;
