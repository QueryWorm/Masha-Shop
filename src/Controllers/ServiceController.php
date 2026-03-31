<?php
class ServiceController {
    public function index() {
        $services = Service::all();
        return View::render('services/index', [
            'title'    => 'Услуги',
            'services' => $services,
        ]);
    }

    public function show(Request $request, string $slug) {
        $service = Service::findBySlug($slug);
        if (!$service) {
            return "404 — услуга не найдена";
        }
        return View::render('services/show', [
            'title'   => $service['title'],
            'service' => $service,
        ]);
    }
}