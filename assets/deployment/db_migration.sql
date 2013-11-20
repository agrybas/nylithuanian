SELECT DISTINCT a.id, a.pagetitle, a.createdon, a.editedon, a.pub_date, a.unpub_date, (SELECT value from nylt_site_tmplvar_contentvalues WHERE contentid=a.id ORDER BY value DESC LIMIT 1) as image, (SELECT value from nylt_site_tmplvar_contentvalues WHERE contentid=a.id ORDER BY value LIMIT 1) as start_date from nylt_site_content a JOIN nylt_site_tmplvar_contentvalues b ON a.id=b.contentid where parent=20 LIMIT 10;
