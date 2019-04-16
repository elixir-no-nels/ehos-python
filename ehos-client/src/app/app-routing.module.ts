import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { CloudsComponent }      from './clouds/clouds.component';
import { NodesComponent }      from './nodes/nodes.component';
//import { DashboardComponent }   from './dashboard/dashboard.component';
//import { HeroDetailComponent }  from './hero-detail/hero-detail.component';

const routes: Routes = [
  { path: '', redirectTo: '/clouds', pathMatch: 'full' },
  { path: 'clouds', component: CloudsComponent },
  { path: 'nodes', component: NodesComponent },
//  { path: 'dashboard', component: DashboardComponent },
//  { path: 'detail/:id', component: HeroDetailComponent },
];

@NgModule({

  imports: [ RouterModule.forRoot(routes) ],

  exports: [ RouterModule ]
})

export class AppRoutingModule {}

