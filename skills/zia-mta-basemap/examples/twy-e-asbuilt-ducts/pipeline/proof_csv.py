"""Machine-readable proof pack accompanying the deck."""
import sys, json, csv, math, collections
sys.path.insert(0, __import__("os").environ.get("ZIA_BASEMAP_SCRIPTS", "../../../scripts"))
import numpy as np
from scipy.spatial import cKDTree
from basemap import load_fixtures
from ducts import FRAME
from register import apply, CORRIDOR

reg=json.load(open('registration.json')); sd=json.load(open('sheet_ducts.json'))
top=json.load(open('topology.json')); deckall=json.load(open('deck_fittings.json'))

with open('duct_schedule.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['sheet','source_layer','segments','on_sheet_length_m','approx_geometry_segments'])
    for loc in ('LOC-01','LOC-02','LOC-03'):
        agg=collections.defaultdict(lambda:[0,0.0,0])
        for it in sd[loc]['ducts']:
            a=agg[it['leaf']]; a[0]+=1; a[1]+=it['clipped_m']; a[2]+=it['approx']
        for k in sorted(agg,key=lambda k:-agg[k][1]):
            w.writerow([loc,k,agg[k][0],round(agg[k][1],2),agg[k][2]])

with open('duct_segments.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['sheet','source_layer','source_xref','approx_geometry',
                                 'on_sheet_length_m','wkt_zia_local_grid_m'])
    for loc in ('LOC-01','LOC-02','LOC-03'):
        for it in sd[loc]['ducts']:
            wkt='LINESTRING('+', '.join(f'{x:.4f} {y:.4f}' for x,y in it['coords'])+')'
            w.writerow([loc,it['leaf'],it['xref'],it['approx'],round(it['clipped_m'],3),wkt])

with open('registration.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['sheet','fitting_symbols_in_frame','matched_within_50mm',
        'fit_rms_m','fit_max_residual_m','holdout_rms_m','holdout_pairs',
        'scale_emu_per_m','frame_ground_span_m','rotation_deg','y_reflected',
        'window_xmin','window_ymin','window_xmax','window_ymax'])
    for loc in ('LOC-01','LOC-02','LOC-03'):
        r=reg[loc]; wd=r['window']
        w.writerow([loc,r['in_frame'],r['in_frame_exact50mm'],round(r['rms'],6),
            round(r['maxres'],6),round(r['holdout_rms'],6),r['holdout_n'],
            round(1/r['s'],1),round(FRAME['w']*r['s'],2),round(math.degrees(r['theta']),6),
            r['reflect'],round(wd[0],3),round(wd[1],3),round(wd[2],3),round(wd[3],3)])

with open('spur_schedule.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['sheet','derived_spur_length_m','segments_chained',
        'terminates_at_asset_type','terminates_at_source_layer','offset_to_fixture_m',
        'hub_source_layer','snap_tolerance_m'])
    for loc in ('LOC-01','LOC-02','LOC-03'):
        for s in sorted(top[loc]['runs'], key=lambda z:-z['length_m']):
            w.writerow([loc,s['length_m'],s['hops'],s['end_type'],s['end_fixture'],
                        s['end_dist'],s['hub_layer'],0.30])

fx=load_fixtures(assets_only=False).reset_index(drop=True)
tree=cKDTree(fx[['x','y']].to_numpy(float))
with open('fitting_match.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['sheet','deck_asset_id','deck_symbol_type','in_plot_frame',
        'registered_x_local','registered_y_local','nearest_source_fixture_layer',
        'nearest_source_block','nearest_source_x','nearest_source_y','residual_m'])
    for loc in ('LOC-01','LOC-02','LOC-03'):
        r=reg[loc]; T=dict(s=r['s'],theta=r['theta'],t=np.array(r['t']),reflect=r['reflect'])
        D=np.array([[p['px'],p['py']] for p in deckall[loc]],float); Q=apply(T,D)
        dd,mi=tree.query(Q)
        for p,q,d,m in zip(deckall[loc],Q,dd,mi):
            inside=(FRAME['x']<=p['px']<=FRAME['x']+FRAME['w'] and
                    FRAME['y']<=p['py']<=FRAME['y']+FRAME['h'])
            g=fx.iloc[m]
            w.writerow([loc,p['asset'],p['type'],inside,round(q[0],4),round(q[1],4),
                        g.leaf,g.block,round(g.x,4),round(g.y,4),round(float(d),4)])
print('wrote duct_schedule.csv duct_segments.csv registration.csv spur_schedule.csv fitting_match.csv')
